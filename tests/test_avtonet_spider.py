import pytest
import requests

from tests import mocks
from news_crawlers import spiders


@pytest.fixture(name="avtonet_spider")
def avtonet_spider_fixture() -> spiders.AvtonetSpider:
    return spiders.AvtonetSpider({"test_url": "dummy_url"})


def test_avtonet_spider_finds_expected_listings(avtonet_spider, monkeypatch):
    monkeypatch.setattr(requests, "get", mocks.mock_requests_get)
    listings = avtonet_spider.run()

    assert len(listings) == 2
