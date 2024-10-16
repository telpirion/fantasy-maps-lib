# Copyright 2024 Google LLC
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
from typing import Iterable, Union, Dict
import math
import random

from fantasy_maps.image.extract import convert_image_to_hash
from fantasy_maps.image.image_metadata import ImageMetadata


def compute_shard_coordinates(
    *,
    img_metadata: ImageMetadata,
    num_shards: int,
    shard_cols: int = 20,
    shard_rows: int = 20,
) -> Union[Iterable[tuple[int, int, int, int, int, int]], None]:
    """Converts an image into smaller images (shards).

    Arguments:
        img_metadata: the metadata of the source image
        num_shards: the number of shards to create
        shard_cols: the number of columns in resulting shards
        shard_rows: the number of rows in resulting shards

    Returns:
        List of tuples of (xMin, yMin, xMax, yMax, columns, rows)
    """
    columns = img_metadata.columns
    rows = img_metadata.rows
    cell_width = img_metadata.cell_width
    cell_height = img_metadata.cell_height
    total_cells = rows * columns

    if shard_cols * shard_rows > total_cells:
        return None

    shards = []
    if rows < shard_rows:
        shard_rows = rows

    if columns < shard_cols:
        shard_cols = columns

    for _ in range(0, num_shards):
        start_col = random.randint(0, columns - shard_cols)
        start_row = random.randint(0, rows - shard_rows)
        x_min = start_col * cell_width
        y_min = start_row * cell_height
        x_max = (start_col + shard_cols) * cell_width
        y_max = (start_row + shard_rows) * cell_height
        shards.append(
            (
                x_min,
                y_min,
                x_max,
                y_max,
                shard_cols,
                shard_rows,
            )
        )

    return shards


def create_shard(
    *,
    x_min: int,
    y_min: int,
    x_max: int,
    y_max: int,
    cols: int,
    rows: int,
    parent_img: ImageMetadata,
) -> Union[ImageMetadata, None]:
    """Crops and saves an image.

    Arguments:
        x_min (int): the left-most point to crop, relative to the parent image
        y_min (int): the top-most point to crop, relative to the parent image
        x_max (int): the right-most point, relative to the parent image
        y_max (int): the bottom-most point, relative to the parent image
        cols (cols): the grid columns in this shard
        rows (rows): the grid rows in this shard
        parent_img (ImageMetadata): metadata of the parent image

    Returns:
        ImageMetadata object representing the new image shard

    """
    d = None
    try:

        img = Image.open(parent_img.path)
        shard = img.crop((int(x_min), int(y_min), int(x_max), int(y_max)))

        # Get new filepath name
        s_path = create_shard_path(
            path=parent_img.path, x_min=x_min, y_min=y_min, cols=cols,
            rows=rows
        )

        # Get new UID
        uid = convert_image_to_hash(shard.tobytes())

        shard.save(s_path)
        d = ImageMetadata(
            rid=parent_img.rid,
            title=parent_img.title,
            url=parent_img.url,
            width=math.floor(x_max - x_min),
            height=math.floor(y_max - y_min),
            columns=cols,
            rows=rows,
            uid=uid,
            path=s_path,
            is_shard=True,
            parent_uid=parent_img.uid
        )

    except SystemError:
        print(f"Error: {parent_img}, bounds: {x_max},{y_max}")
        return None

    return d


def create_shard_path(
    *, path: str, x_min: int, y_min: int, cols: int, rows: int
) -> str:
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
        New image path as str
    """
    file_name_paths = path.split("/")
    paths = file_name_paths[-1].split(".")
    metadata = f"{math.floor(x_min)}_{math.floor(y_min)}.{cols}x{rows}"
    paths.insert(1, metadata)
    s_path = ".".join(paths)
    file_name_paths[-1] = s_path
    return "/".join(file_name_paths)
