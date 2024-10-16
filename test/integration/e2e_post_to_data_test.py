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
import re

from fantasy_maps.reddit import posts
from fantasy_maps.image import converter, extract, shards
from fantasy_maps.image.image_metadata import ImageMetadata

SUBREDDIT = "battlemaps"
COLUMNS = ["Title", "Post", "ID", "URL"]
ROOT_DIR = 'tmp'
NUM_SHARDS = 3
SHARD_COLS = 15
SHARD_ROWS = 15


def test_end_to_end_post_to_data(reddit_credentials,
                                 tmp_path):
    # region reddit-to-metadata
    actual_reddit_objects = posts.get_reddit_posts(
        reddit_credentials=reddit_credentials, subreddit_name=SUBREDDIT,
        limit=50
    )
    assert actual_reddit_objects

    actual_reddit_dicts = posts.convert_posts_to_dicts(actual_reddit_objects,
                                                       COLUMNS)

    assert actual_reddit_dicts

    actual_img_metadata = [
      ImageMetadata(
          url=d['URL'],
          title=d['Title'],
          rid=d['ID']) for d in actual_reddit_dicts if (
        'jpeg' in d['URL'] and
        re.search(r'\d+x\d+', d['Title'])
      )
    ]

    assert actual_img_metadata
    assert actual_img_metadata[0].title != ""

    # endregion

    # region get-image
    local_reddit_data_dir = tmp_path / "reddit_maps_data"
    local_reddit_data_dir.mkdir()

    hashes = []

    for p in actual_img_metadata:
        url = p.url
        filename = posts.make_nice_filename(p.title)

        if filename == '':
            continue

        path = f'{local_reddit_data_dir}/{filename}'
        uid = extract.download_image_local(url=url, path=path)
        if uid in hashes:
            continue

        hashes.append(uid)

        p.path = path
        p.uid = uid

    assert hashes
    actual_first_img = actual_img_metadata[0]

    assert actual_first_img
    assert actual_first_img.uid != ""
    assert actual_first_img.path != ""

    # endregion

    # region check-first-image
    w, h = extract.get_image_width_and_height(actual_first_img.path)
    assert w > 0
    assert h > 0

    actual_first_img.width = w
    actual_first_img.height = h

    exp = r'\.\d+x\d+\.'
    match = re.search(exp, actual_first_img.path)
    if match:
        dims = match.group()

    cols, rows = [int(d) for d in re.split(r'\.|x', dims) if d != '']

    assert cols > 0
    assert rows > 0

    actual_first_img.columns = cols
    actual_first_img.rows = rows

    # endregion

    # region calculate width, height, rows, columns
    for p in actual_img_metadata:
        if not os.path.exists(p.path):
            continue

        local_path = p.path

        # Get width & height for original image
        w, h = extract.get_image_width_and_height(local_path)

        if w == 0 or h == 0:
            p.is_usable = False
            continue

        p.width = w
        p.height = h

        # Get columns & rows for original image, based upon the name.
        exp = '\.\d+x\d+\.'
        match = re.search(exp, p.path)
        if match:
            dims = match.group()

        cols, rows = [int(d) for d in re.split(r'\.|x', dims) if d != '']
        p.columns = cols
        p.rows = rows

        if (cols * rows) <= 500:
            bboxes = extract.compute_bboxes(img_metadata=p)
            p.bboxes = bboxes
            assert len(bboxes) > 0

    # endregion

    actual_img_metadata = [i for i in actual_img_metadata if i.is_usable]

    assert actual_img_metadata

    actual_big_images = [i for i
                         in actual_img_metadata
                         if (i.columns * i.rows) >= 500]

    assert actual_big_images

    for img_metadata in actual_big_images:
        smaller_images = shards.compute_shard_coordinates(
            img_metadata=img_metadata,
            num_shards=NUM_SHARDS,
            shard_cols=SHARD_COLS,
            shard_rows=SHARD_ROWS)

        for sm_img in smaller_images:
            print(img_metadata.path)
            print(sm_img)
            shard_metadata = shards.create_shard(x_min=sm_img[0],
                                                 y_min=sm_img[1],
                                                 x_max=sm_img[2],
                                                 y_max=sm_img[3],
                                                 cols=sm_img[4],
                                                 rows=sm_img[5],
                                                 parent_img=img_metadata)

            if shard_metadata is None:
                continue

            bboxes = extract.compute_bboxes(img_metadata=shard_metadata)
            shard_metadata.bboxes = bboxes
            actual_img_metadata.append(shard_metadata)

            assert shard_metadata
            assert shard_metadata.uid != ""
            assert shard_metadata.path != ""