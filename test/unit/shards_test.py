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
import pathlib
import pytest

from fantasy_maps.image import shards
from fantasy_maps.image.image_metadata import ImageMetadata


@pytest.fixture
def img() -> ImageMetadata:
    test_image_dir = os.path.join(
        pathlib.Path(__file__).parent.resolve(), "../resources/"
    )
    test_image_url = os.path.join(test_image_dir, "gridded-ruined-keep.jpg")
    return ImageMetadata(
        title='Gridded Ruined Keep',
        rid='dummyID',
        url='dummy-url',
        path=test_image_url,
        width=640,
        height=640,
        cell_width=32,
        cell_height=32,
        columns=20,
        rows=20,
    )


def test_compute_shard_coordinates(img):
    actual_shard_coords = shards.compute_shard_coordinates(
        img_metadata=img, num_shards=2, shard_cols=10, shard_rows=10
    )
    assert actual_shard_coords
    assert len(actual_shard_coords) == 2

    actual_first_shard = actual_shard_coords[0]
    print(actual_first_shard[1])
    assert actual_first_shard
    assert len(actual_first_shard) == 6
    assert actual_first_shard[0] >= 0


def test_create_shard(img):
    actual_shard_dict = shards.create_shard(
        x_min=0,
        x_max=320,
        y_min=0,
        y_max=320,
        img_path=img.path,
        cols=10,
        rows=10,
        parent_id="fakehash1",
    )
    assert actual_shard_dict
    actual_shard_url = actual_shard_dict["Path"]
    assert os.path.exists(actual_shard_url)

    # clean up
    os.remove(actual_shard_url)


def test_create_shard_path(img):
    actual_str = shards.create_shard_path(
        path=img.path, x_min=0, y_min=0, cols=10, rows=10
    )
    assert actual_str != ''
    assert actual_str.index('.jpg') != -1
