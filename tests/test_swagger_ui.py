"""Integration test to check whether swagger ui is available."""

import requests

UI_URL = "http://localhost:7979/ui/"


def test_swagger_ui_200():
    """Test for swagger ui."""
    response = requests.get(
        url=UI_URL
    )
    assert response.status_code == 200
