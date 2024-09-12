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


@pytest.fixture
def img_data_dict_edge():
    return {
        'Title': 'Canal Street [14x20] - 5 variations: canal, rain, festival, cat town, floating market', 'Post': '',
        'ID': '1fecohw', 
        'URL': 'https://i.redd.it/85fbl81s57od1.jpeg',
        'LocalPath': 'reddit_maps_data/canal_street_variations_canal_rain_festival.14x20.jpg',
        'UID': '9cfae11a756703b5c752f89611e08ddaee123149',
        'Width': 560,
        'Height': 800,
        'Columns': 14,
        'Rows': 20,
        'VTT': {
            'cellsOffsetX': 0,
            'cellsOffsetY': 0,
            'imageWidth': 560,
            'imageHeight': 800,
            'cellWidth': 40,
            'cellHeight': 40
        },
        'BBoxes': {'bboxes': []}}


def test_convert_image_to_hash(img_content_bytes):
    actual_hash = extract.convert_image_to_hash(img_content_bytes)
    assert actual_hash


def test_download_image_local(img_resource_dir):
    path = os.path.join(img_resource_dir, "tmp.jpg")
    actual_uid = extract.download_image_local(url=IMG_URL, path=path)
    assert actual_uid


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

    """Calculations for first bounding box:

    In pixels, the min points [(32,32), (64,64)]; thus the bbox should go 1
    pixel around the outside: [(31,31), (65,65)]

    xMin = 31 / 640 = 0.0484375
    yMin = 31 / 640 = 0.0484375
    xMax = 65 / 640 = 0.1015625
    yMax = 65 / 640 = 0.1015625
    """
    actual_first_bbox = actual_bboxes[0]
    expected_x_max = 0.1015625
    expected_y_max = expected_x_max

    assert math.isclose(actual_first_bbox["xMax"], expected_x_max)
    assert math.isclose(actual_first_bbox["yMax"], expected_y_max)
    assert math.isclose(actual_first_bbox["xMin"], 0.0484375)
    assert math.isclose(actual_first_bbox["yMin"], 0.0484375)

    """Calculations for last bounding box:

    In pixels, the min points [(576,576), (608,608)]; thus the bbox should go 1
    pixel around the outside: [(575,575), (609,609)]

    xMin = 575 / 640 = 0.8984375
    yMin = 575 / 640 = 0.8984375
    xMax = 609 / 640 = 0.9515625
    yMax = 609 / 640 = 0.9515625
    """
    actual_last_bbox = actual_bboxes[-1]
    expected_x_min = expected_y_min = 0.8984375
    expected_x_max = expected_y_max = 0.9515625
    assert math.isclose(actual_last_bbox["xMax"], expected_x_max)
    assert math.isclose(actual_last_bbox["yMax"], expected_y_max)
    assert math.isclose(actual_last_bbox["xMin"], expected_x_min)
    assert math.isclose(actual_last_bbox["yMin"], expected_y_min)
