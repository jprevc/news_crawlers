from abc import ABC, abstractmethod
import sys
import inspect
from typing import Type

import bs4
import requests

from news_crawlers import configuration


class Spider(ABC):
    def __init__(self, config: configuration.NewsCrawlerConfig) -> None:
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def run(self) -> set:
        pass


class AvtonetSpider(Spider):
    name = "avtonet"

    def run(self) -> set:
        for url in self.config.urls.values():
            avtonet_html = requests.get(url, allow_redirects=False, timeout=10).text

            avtonet_content = bs4.BeautifulSoup(avtonet_html, "html.parser")
            # avtonet_content.select()

        return {}


def get_spider_by_name(name: str) -> Type[Spider]:
    """
    Finds spider class with the 'name' attribute equal to the one specified.

    :param name: Value of the 'name' attribute within the spider class to match.

    :return: Spider class.

    :raises KeyError: If spider could not be found.
    """
    for _, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Spider) and obj.name == name:
            return obj
    raise KeyError(f"Could not find spider with name attribute set to {name}.")
