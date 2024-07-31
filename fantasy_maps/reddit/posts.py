import numpy as np
import pandas as pd
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


def convert_posts_to_dataframe(posts, columns):
    """Convert a list of Reddit posts into a pandas.Dataframe.

    Arguments:
        posts (list): a list of Reddit posts
        columns: the columns to use for the Dataframe

    Returns:
        a pandas.Dataframe
    """

    filtered_posts = [[s.title, s.selftext, s.id, s.url] for s in posts]
    filtered_posts = np.array(filtered_posts)
    reddit_posts_df = pd.DataFrame(filtered_posts, columns=columns)

    return reddit_posts_df


def make_nice_filename(name):
    """Converts Reddit post title into a meaningful(ish) filename.

    Arguments:
        name (str): title of the post

    Returns:
        String. Format is `<adj.>-<nouns>.<cols>x<rows>.jpg`
    """

    dims = re.findall("\d+x\d+", name)
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

    return f"{new_name}.{dims[0]}x{dims[1]}.jpg"


def get_tokens(title):
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
