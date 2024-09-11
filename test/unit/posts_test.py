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

import pytest

from fantasy_maps.reddit import posts


@pytest.fixture
def post_name():
    return 'Unmarked Mine [35x49] - Battlemap/ Dungeon	'


def test_posts_make_nice_filename(post_name):
    actual_filename = posts.make_nice_filename(post_name)

    assert actual_filename
    assert '/' not in actual_filename
