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
from typing import Mapping, List, Union

import praw
import spacy

import re


def get_reddit_posts(reddit_credentials, subreddit_name, limit):
    """Gets the top (hot) posts from a subreddit.

    Arguments:
        reddit_credentials (dict): a dictionary with client_id, secret, and
          user_agent
        subreddit_name (str): the name of the subreddit to scrape posts from
        limit (int): the maximum number of posts to grab

    Returns:
        List of Reddit API objects
    """

    reddit = praw.Reddit(
        client_id=reddit_credentials["client_id"],
        client_secret=reddit_credentials["secret"],
        user_agent=reddit_credentials["user_agent"],
    )

    return reddit.subreddit(subreddit_name).hot(limit=limit)


def convert_posts_to_dicts(
        posts,
        columns
        ) -> Union[List[Mapping[str, str]], None]:
    """Convert a list of Reddit posts into a pandas.Dataframe.

    Arguments:
        posts (list): a list of Reddit posts
        columns: the keys to use for the dicts; maximum of 4

    Returns:
        List of dicts
    """
    if len(columns) != 4:
        return None
    filtered_posts = [
        {columns[0]: s.title,
         columns[1]: s.selftext,
         columns[2]: s.id,
         columns[3]: s.url} for s in posts]
    return filtered_posts


def make_nice_filename(name: str) -> str:
    """Converts Reddit post title into a meaningful(ish) filename.

    Arguments:
        name (str): title of the post

    Returns:
        String. Format is `<adj.>-<nouns>.<cols>x<rows>.jpg`
    """

    dims = re.findall('\d+x\d+', name)
    if len(dims) == 0:
        return ""

    dims = dims[0].split("x")
    if len(dims) != 2:
        return ""

    tokens = get_tokens(name)
    new_name = name.lower()[:30]

    if len(tokens) > 0:
        tokens = tokens[:6]  # Arbitrarily keep new names to six words or less
        new_name = "_".join(tokens)

    # Remove any sensitive characters
    new_name = re.sub(r'[\/|;|\']+', '', new_name)

    return f"{new_name}.{dims[0]}x{dims[1]}.jpg"


def get_tokens(title: str) -> List[str]:
    """Analyzes a post for nouns, proper nouns, and adjectives.

    Arguments:
        title (str): title of the post

    Returns:
        List of string. Words to use in a filename.
    """
    POS = ["PROPN", "NOUN", "ADJ"]

    spacy.prefer_gpu()
    nlp = spacy.load("en_core_web_sm")

    words = []

    tokens = nlp(title)
    for t in tokens:
        pos = t.pos_

        if pos in POS:
            words.append(t.text.lower())

    return words
