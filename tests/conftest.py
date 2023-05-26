import pytest
import requests
from tests import mocks


@pytest.fixture(name="mock_request_avtonet")
def mock_request_avtonet_fixture(monkeypatch):
    monkeypatch.setattr(requests, "get", mocks.mock_requests_get("avtonet_test_html.html"))
