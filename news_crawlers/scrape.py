"""
Main module. Runs defined crawler and send notifications to user, if any news are found.
"""

import os
import json
import argparse

import yaml

from news_crawlers import notificators
from news_crawlers import spiders
from news_crawlers import configuration


def get_cached_items(cached_items_path: str) -> list:
    """
    Returns cached (previously scraped) items from file.

    :param cached_items_path: Path to file which contains items, that were scraped
                              in the previous run.

    :return: List of cached items. If specified file does not exist, an empty list
                                   will be returned.
    """
    if os.path.exists(cached_items_path):
        with open(cached_items_path, encoding="utf8") as file:
            cached_data = json.load(file)
    else:
        cached_data = []

    return cached_data


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="News Crawlers",
        description="Runs web crawlers which will check for updates and alert users if " "there are any news.",
    )
    parser.add_argument("-c", "--config", default="news_crawlers.yaml")
    parser.add_argument("--cache", default=".nc_cache")

    args = parser.parse_args()

    # create __cache__ folder in which *_cache.json files will be stored
    if not os.path.exists(args.cache):
        os.makedirs(args.cache)

    # read configuration
    with open(args.config, encoding="utf8") as file:
        spider_configuration_dict = yaml.safe_load(file)

    for spider_name, spider_config_dict in spider_configuration_dict.items():

        spider_configuration = configuration.NewsCrawlerConfig(**spider_config_dict)

        spider = spiders.get_spider_by_name(spider_name)(spider_configuration)

        # run spider to acquire crawled data
        crawled_data = spider.run()

        # get previously crawled cached items
        cached_json = os.path.join(args.cache, spider_name + "_cached.json")
        cached_spider_data = get_cached_items(cached_json)

        # check which crawled items are new
        new_data = [item for item in crawled_data if item not in cached_spider_data]

        # if new items have been found, send a notification and add that data to cached items
        if new_data:
            # send message with each configured notificator
            for (notificator_type_str, notificator_data) in spider_configuration.notifications.items():
                notificator = notificators.get_notificator_by_name(notificator_type_str)(notificator_data)

                notificator.send_items(
                    spider_name + " news",
                    new_data,
                    notificator_data["message_body_format"],
                    send_separately=notificator_data.get("send_separately", False),
                )

                # append new items to cached ones and write all back to file
                cached_spider_data += list(new_data)
                with open(cached_json, "w+", encoding="utf8") as file:
                    json.dump(cached_spider_data, file)


if __name__ == "__main__":
    main()
