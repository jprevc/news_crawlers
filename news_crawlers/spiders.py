from __future__ import annotations

import os
from abc import ABC, abstractmethod
import sys
import inspect
from typing import Callable

import bs4
import requests


class Spider(ABC):
    def __init__(self, queries: dict[str, str]) -> None:
        """
        Constructs a spider. Spider has a "run" method, which will crawl all set queries when invoked.

        :param queries: Query name and url pairs to be crawled.
        """
        self.queries = queries

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name for the spider. This name is used when referring to spiders in the configuration files or when calling
        the spiders from the CLI.
        """

    @abstractmethod
    def run(self) -> list[dict]:
        """
        Runs crawling on all set queries.
        """


class AvtonetSpider(Spider):
    name = "avtonet"

    def run(self) -> list[dict]:
        found_listings = []
        for query, url in self.queries.items():
            avtonet_html = get_html_from_url(url)

            avtonet_content = bs4.BeautifulSoup(avtonet_html, "html.parser")

            for listing in avtonet_content.select("div[class*=GO-Results-Row]"):
                listing_title = listing.select("div[class*=GO-Results-Naziv]")[0].select("span")[0].text
                listing_href = listing.select("a[class*=stretched-link]")[0].attrs["href"]
                listing_price = listing.select("div[class*=GO-Results-Price-TXT-Regular]")[0].text.strip()

                listing_dict = {
                    "query": query,
                    "title": listing_title,
                    "url": listing_href,
                    "price": listing_price,
                }

                found_listings.append(listing_dict)

        return found_listings


class CarobniSvetSpider(Spider):
    name = "carobni_svet"

    @staticmethod
    def _get_images(bs_content: bs4.BeautifulSoup) -> list[dict]:

        image_elements = bs_content.select("ul[id=images]")[0].select("img")

        image_urls = [image.get("data-original-src") for image in image_elements]

        return [{"type": "image", "data": image_url} for image_url in image_urls]

    @staticmethod
    def _get_blog(bs_content: bs4.BeautifulSoup) -> list[dict]:
        blog_element = bs_content.select("div[id=blogs]")[0]

        text = ""

        text += blog_element.select("div[class=bodyBesedilo]")[0].text
        text += blog_element.select("div[class=bodyBesedilo14]")[0].text
        text += blog_element.select("div[class=bodyBesedilo14]")[1].text

        return [{"type": "blog", "data": text}]

    def run(self) -> list[dict]:
        login_url = "https://carobni-svet.com/portal/parents/login"
        login_info = {"email": os.environ["CS_EMAIL"], "password": os.environ["CS_PASS"]}

        query_to_handler_map: dict[str, Callable[[bs4.BeautifulSoup], list[dict]]] = {
            "photos": self._get_images,
            "blog": self._get_blog,
        }

        found_items = []
        with requests.Session() as session:
            login_response = session.post(login_url, data=login_info)
            assert login_response.ok

            for query, url in self.queries.items():
                carobni_svet_html = session.get(url, timeout=10).text
                carobni_svet_bs = bs4.BeautifulSoup(carobni_svet_html, "html.parser")

                found_items += query_to_handler_map[query](carobni_svet_bs)

        return found_items


class BolhaSpider(Spider):

    name = "bolha"

    def run(self) -> list[dict]:

        found_items: list[dict[str, str]] = []

        for query_name, query_url in self.queries.items():

            # crawl initial page
            html = get_html_from_url(query_url)
            found_items.extend(self._get_items_from_current_page(html, query_name))

            current_page_ind = 2
            while True:
                if current_page_ind > 1000:
                    raise RuntimeError("Something has gone wrong, to many iterations have been performed.")

                # crawl initial page
                try:
                    html = get_html_from_url(f"{query_url}&page={current_page_ind}")
                except ConnectionRefusedError:
                    break

                found_items_on_current_page = self._get_items_from_current_page(html, query_name)

                if not found_items_on_current_page:
                    break

                found_items.extend(found_items_on_current_page)

                current_page_ind += 1

        return found_items

    @staticmethod
    def _get_items_from_current_page(html: str, query_name: str) -> list[dict]:
        bolha_bs = bs4.BeautifulSoup(html, features="html.parser")

        listings = bolha_bs.select("li.EntityList-item")

        found_items: list[dict[str, str]] = []
        for listing in listings:
            listing_el = listing.select("a.link")
            price_el = listing.select("strong.price")

            if not listing_el or not price_el:
                continue

            title = listing_el[0].text
            url = listing_el[0].attrs["href"]

            if not url.startswith("https://www.bolha.com"):
                url = "https://www.bolha.com" + url

            price = price_el[0].get_text(strip=True)

            found_items.append({"query": query_name, "title": title, "price": price, "url": url})

        return found_items


def get_html_from_url(url: str) -> str:
    headers = {
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
        "56.0.2924.87 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        raise ConnectionRefusedError("Page is not accessible")

    return response.text


def get_spider_by_name(name: str) -> type[Spider]:
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
