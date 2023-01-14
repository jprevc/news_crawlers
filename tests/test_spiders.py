import pytest

from news_crawlers import spiders


def test_get_spider_by_name() -> None:
    assert spiders.get_spider_by_name("avtonet") == spiders.AvtonetSpider


def test_get_spider_by_name_raises_key_error_if_spider_not_found() -> None:
    with pytest.raises(KeyError):
        assert spiders.get_spider_by_name("notexistingspider")
