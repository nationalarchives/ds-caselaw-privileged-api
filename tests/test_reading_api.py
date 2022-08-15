# coding: utf-8

import pytest

from fastapi.testclient import TestClient


@pytest.mark.xfail(reason="Test is TODO")
def test_get_document_by_uri(client: TestClient):
    """Test case for get_document_by_uri

    Read a judgment or decision, given its URI
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "GET",
        "/{judgmentUri}".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.xfail(reason="Test is TODO")
def test_judgment_uri_metadata_get(client: TestClient):
    """Test case for judgment_uri_metadata_get

    Gets the document's metadata
    """

    headers = {
        "Authorization": "BasicZm9vOmJhcg==",
    }
    response = client.request(
        "GET",
        "/{judgmentUri}/metadata".format(judgmentUri="judgment_uri_example"),
        headers=headers,
    )

    assert response.status_code == 200
