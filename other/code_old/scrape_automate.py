import google_play_scraper
from google_play_scraper import Sort, reviews_all, search
from google_play_scraper.constants.element import ElementSpecs
from google_play_scraper.constants.regex import Regex
from google_play_scraper.constants.request import Formats
from google_play_scraper.utils.request import post

import pandas as pd
from tqdm import tqdm
import time
import json
from time import sleep
from typing import List, Optional, Tuple

MAX_COUNT_EACH_FETCH = 999

class _ContinuationToken:
    __slots__ = (
        "token", "lang", "country", "sort", "count", "filter_score_with", "filter_device_with",
    )

    def __init__(self, token, lang, country, sort, count, filter_score_with, filter_device_with):
        self.token = token
        self.lang = lang
        self.country = country
        self.sort = sort
        self.count = count
        self.filter_score_with = filter_score_with
        self.filter_device_with = filter_device_with

# Fetch reviews dynamically based on app ID
def _fetch_review_items(
    url: str, app_id: str, sort: int, count: int, filter_score_with: Optional[int],
    filter_device_with: Optional[int], pagination_token: Optional[str]
):
    dom = post(
        url,
        Formats.Reviews.build_body(
            app_id, sort, count,
            "null" if filter_score_with is None else filter_score_with,
            "null" if filter_device_with is None else filter_device_with,
            pagination_token,
        ),
        {"content-type": "application/x-www-form-urlencoded"},
    )
    match = json.loads(Regex.REVIEWS.findall(dom)[0])
    return json.loads(match[0][2])[0], json.loads(match[0][2])[-2][-1]

def reviews(
    app_id: str, lang: str = "en", country: str = "us", sort: Sort = Sort.MOST_RELEVANT,
    count: int = 100, filter_score_with: int = None, filter_device_with: int = None,
    continuation_token: _ContinuationToken = None
) -> Tuple[List[dict], _ContinuationToken]:
    sort = sort.value
    if continuation_token is not None:
        token = continuation_token.token
        if token is None:
            return [], continuation_token
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
                url, app_id, sort, _fetch_count, filter_score_with, filter_device_with, token
            )
        except (TypeError, IndexError):
            token = continuation_token.token
            continue
        for review in review_items:
            result.append({k: spec.extract_content(review) for k, spec in ElementSpecs.Review.items()})
        _fetch_count = count - len(result)
        if isinstance(token, list):
            token = None
            break
    return result, _ContinuationToken(token, lang, country, sort, count, filter_score_with, filter_device_with)

def reviews_all(app_id: str, sleep_milliseconds: int = 0, **kwargs) -> list:
    kwargs.pop("count", None)
    kwargs.pop("continuation_token", None)
    continuation_token = None
    result = []
    while True:
        _result, continuation_token = reviews(
            app_id, count=MAX_COUNT_EACH_FETCH, continuation_token=continuation_token, **kwargs
        )
        result += _result
        if continuation_token.token is None:
            break
        if sleep_milliseconds:
            sleep(sleep_milliseconds / 1000)
    return result

# Function to get app ID by app name
def get_app_id(app_name):
    search_results = search(app_name)
    if len(search_results) > 0:
        app_id = search_results[0]['appId']
        print(f"Found app: {search_results[0]['title']} (ID: {app_id})")
        return app_id
    else:
        print("No app found with that name.")
        return None

# Main scraping function
def scrape_app_reviews(app_name, reviews_count=5000, country='us', lang='en'):
    app_id = get_app_id(app_name)
    if app_id is None:
        return
    print(f"Scraping reviews for {app_name} ({app_id})...\n")
    result = []
    continuation_token = None
    with tqdm(total=reviews_count, position=0, leave=True) as pbar:
        while len(result) < reviews_count:
            new_result, continuation_token = reviews(
                app_id, continuation_token=continuation_token, lang=lang, country=country,
                sort=Sort.NEWEST, filter_score_with=None, count=199
            )
            if not new_result:
                break
            result.extend(new_result)
            pbar.update(len(new_result))
    reviews_df = pd.DataFrame(result)
    reviews_df['app_name'] = app_name
    reviews_df.to_csv(f"{app_name}_reviews.csv", index=False)
    print(f"\nCompleted downloading {len(reviews_df)} reviews for {app_name}.\n")

# User input loop
if __name__ == "__main__":
    while True:
        app_name = input("Enter the name of the app to download reviews for (or 'exit' to quit): ").strip()
        if app_name.lower() == 'exit':
            break
        scrape_app_reviews(app_name)
