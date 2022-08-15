# coding: utf-8

from fastapi.testclient import TestClient


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
    # assert response.status_code == 200
