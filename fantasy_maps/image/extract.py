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

import hashlib
import math
import requests

from .image_metadata import ImageMetadata, BBox


def convert_image_to_hash(content: str) -> str:
    """Convert image data to hash value (str).

    Arguments:
        content (byte array): the image

    Return:
        Bool. Indicates whether the process was success.
    """

    sha1 = hashlib.sha1()
    sha1.update(content)
    jpg_hash = sha1.hexdigest()

    return jpg_hash


def download_image_local(*, url: str, path: str) -> str:
    """Download an image from the internet to local file system.

    Arguments:
        url (str): the image to download
        path (str): the local path to save the image.

    Returns:
        Hash value (str) of image file
    """

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        uid = convert_image_to_hash(r.content)

        with open(path, "wb") as f:
            f.write(r.content)

        return uid

    return ""


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


def compute_bboxes(
    *,
    img_metadata: ImageMetadata,
):
    """Determines bounding boxes for image object detection.

    Arguments:
        img_data_dict: a dict containing width, height, columns, rows of an img
        cell_width (int): the width of cells in the image
        cell_height (int): the height of cells in the image

    Returns:
        List of dict with dimensions of each cell "normalized" in COCO format:
        represented as a percentage of total width or height.
    """
    bboxes = []
    try:
        if img_metadata:
            width = img_metadata.width
            height = img_metadata.height
            columns = img_metadata.columns
            rows = img_metadata.rows
            cell_width = img_metadata.cell_width
            cell_height = img_metadata.cell_height
        else:
            return bboxes

        BORDER = 1  # 1px border around the outside of the cell
        LABEL = "cell"

        x_coords = []
        curr_x_min = cell_width - BORDER
        curr_x_max = (2 * cell_width) + BORDER
        for _ in range(0, columns - 2):
            x_coords.append(
                {
                    "xMin": curr_x_min / width,
                    "xMax": curr_x_max / width,
                }
            )
            curr_x_min += cell_width
            curr_x_max += cell_width

        curr_y_min = cell_height - BORDER
        curr_y_max = (2 * cell_height) + BORDER
        for _ in range(0, rows - 2):
            tmp_bboxes = [
                BBox(
                    x_max=x["xMax"],
                    x_min=x["xMin"],
                    y_max=curr_y_max / height,
                    y_min=curr_y_min / height,
                    label=LABEL,
                )
                for x in x_coords
            ]
            bboxes = bboxes + tmp_bboxes
            curr_y_min += cell_height
            curr_y_max += cell_height

    except Exception:
        print(f"Error: {img_metadata}")

    return bboxes
