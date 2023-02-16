import json
import pathlib
import re

import requests
import pytest

from news_crawlers.__main__ import main
from tests import mocks

# pylint: disable=unused-argument


@pytest.fixture(name="dummy_config")
def dummy_config_fixture(tmp_path: pathlib.Path):
    _create_dummy_config(tmp_path / "news_crawlers.yaml", {"spiders": {}})


@pytest.fixture(name="avtonet_dummy_config")
def avtonet_dummy_config_fixture(tmp_path: pathlib.Path):
    _create_dummy_config(
        tmp_path / "news_crawlers.yaml", {"spiders": {"avtonet": {"urls": {"dummy_url": ""}, "notifications": {}}}}
    )


def _create_dummy_config(path, content_dict):
    with open(path, "w+", encoding="utf-8") as file:
        json.dump(content_dict, file)


def test_main_basic(capsys):
    with pytest.raises(SystemExit):
        main(("--help",))

    _, err = capsys.readouterr()

    assert err == ""


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(("--version",))

    out, _ = capsys.readouterr()

    assert re.match(r"(\d\.){2}\d", out)


def test_log_option_creates_log_file(dummy_config, tmp_path: pathlib.Path):
    log_path = tmp_path / "news_crawlers.log"
    main(("scrape", "--config", str(tmp_path / "news_crawlers.yaml")))

    assert not log_path.exists()

    main(("--log", str(log_path), "scrape", "--config", str(tmp_path / "news_crawlers.yaml")))

    assert log_path.exists()


def test_running_scrape_command_returns_expected_items(monkeypatch, tmp_path: pathlib.Path, avtonet_dummy_config):
    monkeypatch.setattr(requests, "get", mocks.mock_requests_get)

    main(
        (
            "scrape",
            "--config",
            str(tmp_path / "news_crawlers.yaml"),
            "--cache",
            str(tmp_path / ".nc_cache"),
            "-s",
            "avtonet",
        )
    )

    cache_file = tmp_path / ".nc_cache" / "avtonet_cached.json"
    assert cache_file.exists()

    with open(cache_file, encoding="utf8") as cache_file:
        listings = json.load(cache_file)

    assert len(listings) == 2
