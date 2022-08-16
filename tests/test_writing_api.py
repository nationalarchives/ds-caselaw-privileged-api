# coding: utf-8

import pytest
from fastapi.testclient import TestClient


@pytest.mark.xfail(reason="Test is TODO")
def test_judgment_uri_lock_get(client: TestClient):
    """Test case for judgment_uri_lock_get

    Query lock status for a document
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "GET",
        "/{judgmentUri}/lock".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200


@pytest.mark.xfail(reason="Test is TODO")
def test_judgment_uri_lock_put(client: TestClient):
    """Test case for judgment_uri_lock_put

    Lock access to a document
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "PUT",
        "/{judgmentUri}/lock".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200


@pytest.mark.xfail(reason="Test is TODO")
def test_judgment_uri_metadata_patch(client: TestClient):
    """Test case for judgment_uri_metadata_patch

    Set document properties
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "PATCH",
        "/{judgmentUri}/metadata".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200


@pytest.mark.xfail(reason="Test is TODO")
def test_judgment_uri_put(client: TestClient):
    """Test case for judgment_uri_put

    Update a judgment
    """

    headers = {
        "if_match": "1",
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "PUT",
        "/{judgmentUri}".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    assert response.status_code == 200
