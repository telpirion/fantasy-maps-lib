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
from fantasy_maps.reddit import posts

SUBREDDIT = "fantasymaps"
COLUMNS = ["Title", "Post", "ID", "URL"]
POST_NAME = "Old Watermill - Battle Map (30x45)"


def test_get_reddit_posts(reddit_credentials, reddit_posts):
    actual_reddit_objects = posts.get_reddit_posts(
        reddit_credentials=reddit_credentials, subreddit_name=SUBREDDIT,
        limit=50
    )
    assert actual_reddit_objects
    actual_posts = [[s.title, s.selftext, s.id, s.url] for s in
                    actual_reddit_objects]
    assert len(actual_posts) == 50


def test_convert_posts_to_dicts(reddit_posts):
    actual_dicts = posts.convert_posts_to_dicts(reddit_posts, COLUMNS)
    assert actual_dicts
    assert len(actual_dicts) == 2

    actual_first_dict = actual_dicts[0]
    assert actual_first_dict
    assert actual_first_dict[COLUMNS[0]] != ""


def test_make_nice_filename():
    actual_filename = posts.make_nice_filename(POST_NAME)
    assert actual_filename
    assert actual_filename.find("watermill") != -1


def test_get_tokens():
    actual_tokens = posts.get_tokens(POST_NAME)
    assert actual_tokens
    assert len(actual_tokens) > 0
