import pytest
import requests

from tests import mocks
from news_crawlers import spiders


@pytest.fixture(name="mock_request_bolha")
def mock_request_bolha_fixture(monkeypatch):
    monkeypatch.setattr(requests, "get", mocks.mock_requests_get("bolha_test_html.html"))


@pytest.fixture(name="bolha_spider")
def bolha_spider_fixture() -> spiders.BolhaSpider:
    return spiders.BolhaSpider({"test_url": "dummy_url"})


@pytest.mark.usefixtures("mock_request_bolha")
def test_bolha_spider_finds_expected_listings(bolha_spider):
    listings = bolha_spider.run()

    assert len(listings) == 26
