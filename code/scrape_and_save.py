import google_play_scraper
from google_play_scraper import Sort
from google_play_scraper.constants.element import ElementSpecs
from google_play_scraper.constants.regex import Regex
from google_play_scraper.constants.request import Formats
from google_play_scraper.utils.request import post

import pandas as pd
from datetime import datetime
from tqdm import tqdm
import time
import json
from time import sleep
from typing import List, Optional, Tuple

MAX_COUNT_EACH_FETCH = 199

# Define the list of apps and their app IDs
apps = {
    'Netflix': 'com.netflix.mediaclient',
    'Amazon': 'com.amazon.mShop.android.shopping',
    'Snapchat': 'com.snapchat.android',
    'ChatGPT': 'com.openai.chatgpt',
    'Facebook': 'com.facebook.katana'
}

class _ContinuationToken:
    __slots__ = (
        "token",
        "lang",
        "country",
        "sort",
        "count",
        "filter_score_with",
        "filter_device_with",
    )

    def __init__(
        self,
        token,
        lang,
        country,
        sort,
        count,
        filter_score_with,
        filter_device_with
    ):
        self.token = token
        self.lang = lang
        self.country = country
        self.sort = sort
        self.count = count
        self.filter_score_with = filter_score_with
        self.filter_device_with = filter_device_with


def _fetch_review_items(
    url: str,
    app_id: str,
    sort: int,
    count: int,
    filter_score_with: Optional[int],
    filter_device_with: Optional[int],
    pagination_token: Optional[str]
):
    dom = post(
        url,
        Formats.Reviews.build_body(
            app_id, sort, count,
            "null" if filter_score_with is None else filter_score_with,
            "null" if filter_device_with is None else filter_device_with,
            pagination_token
        ),
        {"content-type": "application/x-www-form-urlencoded"},
    )
    match = json.loads(Regex.REVIEWS.findall(dom)[0])

    return json.loads(match[0][2])[0], json.loads(match[0][2])[-2][-1]


def reviews(
    app_id: str, lang: str = "en", country: str = "us",
    sort: Sort = Sort.MOST_RELEVANT, count: int = 100,
    filter_score_with: int = None, filter_device_with: int = None,
    continuation_token: _ContinuationToken = None
) -> Tuple[List[dict], _ContinuationToken]:
    sort = sort.value

    if continuation_token is not None:
        token = continuation_token.token

        if token is None:
            return (
                [],
                continuation_token,
            )

        lang = continuation_token.lang
        country = continuation_token.country
        sort = continuation_token.sort
        count = continuation_token.count
        filter_score_with = continuation_token.filter_score_with
        filter_device_with = continuation_token.filter_device_with
    else:
        token = None

    url = Formats.Reviews.build(lang=lang, country=country)

    _fetch_count = count

    result = []

    while True:
        if _fetch_count == 0:
            break

        if _fetch_count > MAX_COUNT_EACH_FETCH:
            _fetch_count = MAX_COUNT_EACH_FETCH

        try:
            review_items, token = _fetch_review_items(
                url,
                app_id,
                sort,
                _fetch_count,
                filter_score_with,
                filter_device_with,
                token
            )
        except (TypeError, IndexError):
            # MOD: Handle empty token
            token = continuation_token.token
            continue

        for review in review_items:
            result.append(
                {
                    k: spec.extract_content(review)
                    for k, spec in ElementSpecs.Review.items()
                }
            )

        _fetch_count = count - len(result)

        if isinstance(token, list):
            token = None
            break

    return (
        result,
        _ContinuationToken(
            token, lang, country, sort, count, filter_score_with, filter_device_with
        ),
    )


def reviews_all(app_id: str, sleep_milliseconds: int = 0, **kwargs) -> list:
    """Fetch all reviews for a specific app ID."""
    kwargs.pop("count", None)
    kwargs.pop("continuation_token", None)

    continuation_token = None

    result = []

    while True:
        _result, continuation_token = reviews(
            app_id, count=MAX_COUNT_EACH_FETCH, continuation_token=continuation_token,
            **kwargs
        )

        result += _result

        if continuation_token.token is None:
            break

        if sleep_milliseconds:
            sleep(sleep_milliseconds / 1000)

    return result

# Main function to scrape reviews for all apps
def scrape_reviews_for_apps(apps: dict, reviews_count: int = 25000):
    all_reviews = pd.DataFrame()

    # Loop over each app and scrape its reviews
    for app_name, app_id in apps.items():
        result = []
        continuation_token = None

        # Improved display: App name with padding for better visibility
        print(f"\nScraping reviews for {app_name}...\n{'-' * 40}")

        # Customize tqdm progress bar format
        with tqdm(total=reviews_count, position=0, leave=True,
                  desc=f"{app_name} Reviews", unit="review",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:

            while len(result) < reviews_count:
                new_result, continuation_token = reviews(
                    app_id,
                    continuation_token=continuation_token,
                    lang='en',  #The language of review
                    country='us',  #Country for which you want to scrapes
                    sort=Sort.NEWEST,
                    filter_score_with=None,
                    count=199
                )
                if not new_result:
                    break
                result.extend(new_result)
                pbar.update(len(new_result))

        # Create DataFrame for this app's reviews and append app name
        app_reviews = pd.DataFrame(result)
        app_reviews['app_name'] = app_name

        # Combine with all reviews
        all_reviews = pd.concat([all_reviews, app_reviews], ignore_index=True)

        # Confirmation message
        print(f"\nCompleted scraping for {app_name}. Total reviews scraped: {len(result)}\n")

        # Optional: Add sleep to avoid getting blocked
        sleep(1)

    return all_reviews


# Scrape reviews for all apps and union them into a single DataFrame
reviews_count = 5000  # Set the max number of reviews you want per app
all_reviews = scrape_reviews_for_apps(apps, reviews_count)

# Save the combined DataFrame to a CSV for analysis
all_reviews.to_csv('combined_app_reviews.csv', index=False)

# Inspect the combined data
print(all_reviews.head())
