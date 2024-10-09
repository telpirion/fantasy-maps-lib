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

from fantasy_maps.image import extract, ImageMetadata

IMG_URL = "https://i.redd.it/tnwu13fdki171.jpg"


@pytest.fixture
def img_resource_dir():
    test_image_dir = os.path.join(
        pathlib.Path(__file__).parent.resolve(), "../resources/"
    )
    return test_image_dir


@pytest.fixture
def img(img_resource_dir):
    test_image_url = os.path.join(img_resource_dir, "small_cemetary.17x22.jpg")
    # img_path, width, height, columns, rows
    return ImageMetadata(
        url="dummy-url",
        title="small cemetary [17x22]",
        rid="dummyId",
        path=test_image_url,
        width=564,
        height=729,
    )


@pytest.fixture
def img_content_bytes(img):
    with open(img.path, "rb") as file:
        test_image = file.read()
    return test_image


@pytest.fixture
def img_metadata():
    return ImageMetadata(
        url="https://i.redd.it/85fbl81s57od1.jpeg",
        rid="1fecohw",
        title="""Canal Street [14x20] - 5 variations: canal, rain, festival,
        cat town, floating market""",
        width=560,
        height=800,
        columns=14,
        rows=20,
        uid="9cfae11a756703b5c752f89611e08ddaee123149",
        cell_height=40,
        cell_width=40,
    )


def test_convert_image_to_hash(img_content_bytes):
    actual_hash = extract.convert_image_to_hash(img_content_bytes)
    assert actual_hash


def test_download_image_local(img_resource_dir):
    path = os.path.join(img_resource_dir, "tmp.jpg")
    actual_uid = extract.download_image_local(url=IMG_URL, path=path)
    assert actual_uid


def test_get_image_width_and_height(img):
    width, height = extract.get_image_width_and_height(img.path)
    assert width == img.width
    assert height == img.height


def test_compute_vtt_data(img_metadata):
    actual_vtt = img_metadata.to_vtt()
    assert len(actual_vtt.keys()) == 6
    assert actual_vtt["cellsOffsetX"] == 0
    assert actual_vtt["cellsOffsetY"] == 0
    assert actual_vtt["imageWidth"] == img_metadata.width
    assert actual_vtt["imageHeight"] == img_metadata.height
    assert actual_vtt["cellWidth"] == img_metadata.cell_width
    assert actual_vtt["cellHeight"] == img_metadata.cell_height


def test_compute_bboxes(img_metadata):
    actual_bboxes = extract.compute_bboxes(img_metadata=img_metadata)
    assert len(actual_bboxes) != 0

    actual_first_bbox = actual_bboxes[0]
    expected_x_max = 0.14464285714285716
    expected_y_max = 0.10125
    expected_x_min = 0.06964285714285715
    expected_y_min = 0.04875
    assert math.isclose(actual_first_bbox.x_max, expected_x_max)
    assert math.isclose(actual_first_bbox.y_max, expected_y_max)
    assert math.isclose(actual_first_bbox.x_min, expected_x_min)
    assert math.isclose(actual_first_bbox.y_min, expected_y_min)

    actual_last_bbox = actual_bboxes[-1]
    expected_x_max = 0.9303571428571429
    expected_x_min = 0.8553571428571428
    expected_y_min = 0.89875
    expected_y_max = 0.95125
    assert math.isclose(actual_last_bbox.x_max, expected_x_max)
    assert math.isclose(actual_last_bbox.y_max, expected_y_max)
    assert math.isclose(actual_last_bbox.x_min, expected_x_min)
    assert math.isclose(actual_last_bbox.y_min, expected_y_min)
