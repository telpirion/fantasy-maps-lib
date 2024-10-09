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
from dataclasses import dataclass
import os


@dataclass
class TestPostGeneratorObj:
    title: str
    selftext: str
    id: str
    url: str


@pytest.fixture(scope="session", autouse=True)
def reddit_credentials():
    client_id = os.environ["REDDIT_CLIENT_ID"]
    agent = os.environ["REDDIT_USER_AGENT"]
    secret = os.environ["REDDIT_SECRET"]

    return {
        "client_id": client_id,
        "secret": secret,
        "user_agent": agent,
    }


@pytest.fixture(scope="session", autouse=True)
def reddit_posts():
    class PostIterator:
        def __iter__(self):
            yield TestPostGeneratorObj(
                "Old Watermill - Battle Map (30x45)",
                "",
                "14kb71a",
                "https://i.redd.it/0y3sfrkiqj8b1.jpg",
            )
            yield TestPostGeneratorObj(
                "[OC] The Inn Beyond Worlds - [50x50]",
                "",
                "14kg2c0",
                "https://i.redd.it/ks1wup6drk8b1.jpg",
            )

    return PostIterator()
