import pathlib

import pytest

from news_crawlers import spiders


def mock_requests_get(_: str) -> str:
    mock_html_path = pathlib.Path(__file__).parent / "res" / "avtonet_test_html.html"

    with open(mock_html_path, encoding="utf8") as file:
        html_content = file.read()

    return html_content


@pytest.fixture(name="avtonet_spider")
def avtonet_spider_fixture() -> spiders.AvtonetSpider:
    return spiders.AvtonetSpider({"test_url": "dummy_url"})


def test_avtonet_spider_finds_expected_listings(avtonet_spider, monkeypatch):
    monkeypatch.setattr(avtonet_spider, "_get_raw_html", mock_requests_get)
    listings = avtonet_spider.run()

    assert len(listings) == 2
