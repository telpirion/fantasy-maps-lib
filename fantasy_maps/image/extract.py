# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from PIL import Image

import hashlib
import math
import pandas as pd
import requests


def convert_image_to_hash(content, hashes):
    """Convert image data to hash value (str).

    Arguments:
        content (byte array): the image
        hashes (list): a list of hashes from converted strings

    Return:
        Bool. Indicates whether the process was success.
    """

    sha1 = hashlib.sha1()
    sha1.update(content)
    jpg_hash = sha1.hexdigest()

    if jpg_hash in hashes:
        hashes.append("")
        return False

    hashes.append(jpg_hash)
    return True


def download_image_local(url, path, hashes):
    """Download an image from the internet to local file system.

    Arguments:
        url (str): the image to download
        path (str): the local path to save the image.
        hashes (list): the list of UIDs for downloaded images

    Returns:
        Bool. Indicates whether downloading the image was successful.
    """

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True

        is_unique = convert_image_to_hash(r.content, hashes)
        if not is_unique:
            return False

        with open(path, "wb") as f:
            f.write(r.content)
    else:
        return False

    return True


def get_image_width_and_height(path):
    """Open the image and get the image's height and width in pixels.

    Arguments:
        path (str):

    Returns:
        Tuple of width, height
    """

    img = Image.open(path)
    w, h = img.size

    return (math.floor(w), math.floor(h))


def compute_vtt_data(width, height, columns, rows):
    """Calculate the VTT values for the image.

    Arguments:
        width (int):
        height (int):
        columns (int):
        rows (int):
    Returns:
        Dict.
    """

    return {
        "cellsOffsetX": 0,  # Assumes no offset
        "cellsOffsetY": 0,  # Assumes no offset
        "imageWidth": int(width),
        "imageHeight": int(height),
        "cellWidth": int(width / columns),
        "cellHeight": int(height / rows),
    }


def compute_shard_coordinates(
    width: int,
    height: int,
    cell_width: int,
    cell_height: int,
    columns: int,
    rows: int
):
    """Converts image data into 1,or more shards.

    Arguments:
        width (int):
        height (int):
        cell_width (int):
        cell_height (int):
        columns (int):
        rows (int):

    Returns:
        List of tuples of (xMin, yMin, xMax, yMax, columns, rows)
        TODO: convert to pd.Series
    """

    total_cells = columns * rows
    if total_cells <= 500:
        return

    # Assume that a perfectly square map that approaches 500 cells is 22 cols by 22 rows.
    # Cut an image into as many 22x22 shards as possible
    SQRT = 22

    h_shards = math.floor(columns / SQRT)
    h_rem = columns % SQRT
    v_shards = math.floor(rows / SQRT)
    v_rem = rows % SQRT
    shard_columns = shard_rows = SQRT

    # Edge case 1: we have a narrow width (portrait-oriented) map
    if h_shards == 0:
        h_shards = 1
        h_rem = 0
        shard_columns = columns

    # Edge case 2: we have a short height (landscape-oriented) map
    if v_shards == 0:
        v_shards = 1
        v_rem = 0
        shard_rows = rows

    shards = []
    curr_min_x = 0
    curr_min_y = 0
    for _ in range(h_shards):
        max_x = (cell_width * shard_columns) + curr_min_x
        if max_x > width:
            max_x = width
        for _ in range(v_shards):
            max_y = (cell_height * shard_rows) + curr_min_y
            if max_y > height:
                max_y = height

            shards.append(
                (curr_min_x, curr_min_y, max_x, max_y, shard_columns,
                 shard_rows)
            )
            curr_min_y = max_y

        curr_min_y = 0
        curr_min_x = max_x

    # Get the right-side remainder
    curr_min_x = width - (h_rem * cell_width)
    curr_min_y = 0
    for _ in range(v_shards):
        max_y = (cell_height * shard_rows) + curr_min_y
        if max_y > height:
            max_y = height
        shards.append((curr_min_x, curr_min_y, width, max_y, h_rem, shard_rows))
        curr_min_y = max_y

    # Get the bottom-side remainder
    curr_min_y = height - (v_rem * cell_height)
    curr_min_x = 0
    for _ in range(h_shards):
        max_x = (cell_width * shard_columns) + curr_min_x
        if max_x > width:
            max_x = width
        shards.append((curr_min_x, curr_min_y, max_x, height, shard_columns, v_rem))
        curr_min_x = max_x

    return shards


def create_shard(x_min, y_min, x_max, y_max, cols, rows, img_path, parent_id):
    """Crops and saves an image.

    Arguments:
        x_min (int): the left-most point to crop, relative to the parent image
        y_min (int): the top-most point to crop, relative to the parent image
        x_max (int): the right-most point, relative to the parent image
        y_max (int): the bottom-most poinst, relative to the parent image
        cols (cols): the grid columns in this shard
        rows (rows): the grid rows in this shard
        img_path (str): the parent image's local path
        parent_id (str): the parent image's UID

    Returns:
        DataFrame with local path, UID, width, height, columns, and rows

    """
    try:

        img = Image.open(img_path)
        shard = img.crop((int(x_min), int(y_min), int(x_max), int(y_max)))

        # Get new filepath name
        s_path = create_shard_path(img_path, x_min, y_min, cols, rows)

        # Get new UID
        hashes = []
        convert_image_to_hash(shard.tobytes(), hashes)

        shard.save(s_path)

        d = {
            "Width": math.floor(x_max - x_min),
            "Height": math.floor(y_max - y_min),
            "Columns": cols,
            "Rows": rows,
            "UID": hashes[0],
            "Path": s_path,
            "IsShard": True,
            "Parent": parent_id,
        }

    except SystemError:
        print(f"Error: {img_path}, bounds: {x_max},{y_max}")
        return None

    return pd.DataFrame(data=d, index=[0])


def create_shard_path(path, x_min, y_min, cols, rows):
    """Convert an image path string to new string.

    Assumes the image path is of the format:
        <folder>/<name>.<cols>x<rows>.jpg

    Arguments:
        path (str):
        x_min (int):
        y_min (int):
        cols (int):
        rows (int):

    Returns:
        String. New image path.
    """

    paths = path.split(".")
    paths[-2] = f"{math.floor(x_min)}_{math.floor(y_min)}.{cols}x{rows}"
    s_path = ".".join(paths)
    return s_path


def compute_bboxes(*, dataframe=None, series=None, cell_width=0, cell_height=0):
    """Determines bounding boxes for image object detection.

    Arguments:
        dataframe (pandas.Dataframe): A DataFrame with Height, Width, Columns, and Rows
        series (pandas.Series): A Series with Height, Width, Columns, and Rows
        cell_width (int):
        cell_height (int):

    Returns:
        List of dict.
    """
    bboxes = []
    try:
        if dataframe is not None:
            width = dataframe.iloc[0]["Width"]
            height = dataframe.iloc[0]["Height"]
            columns = dataframe.iloc[0]["Columns"]
            rows = dataframe.iloc[0]["Rows"]
        elif series is not None:
            width = series["Width"]
            height = series["Height"]
            columns = series["Columns"]
            rows = series["Rows"]
        else:
            return bboxes

        BORDER = 1  # 1px border around the outside of the cell
        LABEL = "cell"

        curr_x = cell_width
        while curr_x < width:
            curr_y = cell_height
            while curr_y < height:
                x_min = (curr_x - BORDER) / width
                y_min = (curr_y - BORDER) / height
                x_max = (curr_x + cell_width + BORDER) / width
                y_max = (curr_y + cell_height + BORDER) / height
                bboxes.append(
                    {
                        "xMin": x_min,
                        "xMax": x_max,
                        "yMin": y_min,
                        "yMax": y_max,
                        "displayName": LABEL,
                    }
                )
                curr_y = curr_y + cell_height
            curr_x = curr_x + cell_width
    except Exception:
        print(f"Error: {dataframe}")

    return bboxes