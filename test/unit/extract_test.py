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
import os
import math
import pathlib
import pytest

from fantasy_maps.image import extract

IMG_URL = "https://i.redd.it/tnwu13fdki171.jpg"


@pytest.fixture
def img_resource_dir():
    test_image_dir = os.path.join(
        pathlib.Path(__file__).parent.resolve(), "../resources/"
    )
    return test_image_dir


@pytest.fixture
def img(img_resource_dir):
    test_image_url = os.path.join(img_resource_dir, "gridded-ruined-keep.jpg")
    # img_path, width, height, columns, rows
    return (test_image_url, 640, 640, 20, 20)


@pytest.fixture
def img_content_bytes(img):
    with open(img[0], "rb") as file:
        test_image = file.read()
    return test_image


@pytest.fixture
def hashes():
    return ["fakehash1", "fakehash2"]


@pytest.fixture
def img_data_dict(img):
    return {"width": img[1], "height": img[2], "columns": img[3], "rows": img[4]}


def test_convert_image_to_hash(img_content_bytes, hashes):
    success = extract.convert_image_to_hash(img_content_bytes, hashes)
    assert success
    assert len(hashes) == 3
    actual_new_hash = hashes[2]
    assert actual_new_hash != ""


def test_download_image_local(img_resource_dir, hashes):
    path = os.path.join(img_resource_dir, "tmp.jpg")
    success = extract.download_image_local(url=IMG_URL, path=path, hashes=hashes)
    assert success
    assert len(hashes) == 3
    actual_new_hash = hashes[2]
    assert actual_new_hash != ""


def test_get_image_width_and_height(img):
    width, height = extract.get_image_width_and_height(img[0])
    assert width == img[1]
    assert height == img[2]


def test_compute_vtt_data(img):
    actual_vtt = extract.compute_vtt_data(
        width=img[1], height=img[2], columns=img[3], rows=img[4]
    )
    assert len(actual_vtt.keys()) == 6
    assert actual_vtt["cellsOffsetX"] == 0
    assert actual_vtt["cellsOffsetY"] == 0
    assert actual_vtt["imageWidth"] == img[1]
    assert actual_vtt["imageHeight"] == img[2]
    assert actual_vtt["cellWidth"] == img[1] / img[3]
    assert actual_vtt["cellHeight"] == img[2] / img[4]


def test_compute_bboxes(img, img_data_dict):
    actual_bboxes = extract.compute_bboxes(
        img_data_dict=img_data_dict,
        cell_width=img[1] / img[3],
        cell_height=img[2] / img[4],
    )
    assert len(actual_bboxes) != 0
    actual_first_bbox = actual_bboxes[0]

    """Calculations for first bounding box:

    In pixels, the min points [(32,32), (64,64)]; thus the bbox should go 1 pixel
    around the outside: [(31,31), (65,65)]

    xMin = 31 / 640 = 0.0484375
    yMin = 31 / 640 = 0.0484375
    xMax = 65 / 640 = 0.1015625
    yMax = 65 / 640 = 0.1015625
    """
    expected_xmax = 0.1015625
    expected_ymax = expected_xmax

    assert math.isclose(actual_first_bbox['xMax'], expected_xmax)
    assert math.isclose(actual_first_bbox['yMax'], expected_ymax)
    assert math.isclose(actual_first_bbox['xMin'], 0.0484375)
    assert math.isclose(actual_first_bbox['yMin'], 0.0484375)
