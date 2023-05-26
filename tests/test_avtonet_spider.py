import pytest
import requests

from tests import mocks
from news_crawlers import spiders


@pytest.fixture(name="mock_request_avtonet")
def mock_request_avtonet_fixture(monkeypatch):
    monkeypatch.setattr(requests, "get", mocks.mock_requests_get("avtonet_test_html.html"))


@pytest.fixture(name="avtonet_spider")
def avtonet_spider_fixture() -> spiders.AvtonetSpider:
    return spiders.AvtonetSpider({"test_url": "dummy_url"})


@pytest.mark.usefixtures("mock_request_avtonet")
def test_avtonet_spider_finds_expected_listings(avtonet_spider):
    listings = avtonet_spider.run()

    assert len(listings) == 2
