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
from typing import Mapping

import hashlib
import math
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
        hashes.append('')
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

        with open(path, 'wb') as f:
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
        'cellsOffsetX': 0,  # Assumes no offset
        'cellsOffsetY': 0,  # Assumes no offset
        'imageWidth': int(width),
        'imageHeight': int(height),
        'cellWidth': int(width / columns),
        'cellHeight': int(height / rows),
    }


def compute_bboxes(
        *,
        img_data_dict: Mapping[str, str | int] = None,
        cell_width: int = 0,
        cell_height: int = 0):
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
        if img_data_dict is not None:
            width = img_data_dict['width']
            height = img_data_dict['height']
        else:
            return bboxes

        BORDER = 1  # 1px border around the outside of the cell
        LABEL = 'cell'

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
                        'xMin': x_min,
                        'xMax': x_max,
                        'yMin': y_min,
                        'yMax': y_max,
                        'displayName': LABEL,
                    }
                )
                curr_y = curr_y + cell_height
            curr_x = curr_x + cell_width
    except Exception:
        print(f'Error: {img_data_dict}')

    return bboxes
