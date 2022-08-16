# coding: utf-8

import pytest
from fastapi.testclient import TestClient


@pytest.mark.xfail(reason="Test is TODO")
def test_status_get(client: TestClient):
    """Test case for status_get

    Health check
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "GET",
        "/status",
        headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200
