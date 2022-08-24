# coding: utf-8
from unittest.mock import patch, Mock

import pytest
from caselawclient.Client import MarklogicResourceNotFoundError

from fastapi.testclient import TestClient
from openapi_server.main import app


@patch("openapi_server.apis.reading_api.client_for_basic_auth")
def test_get_success(mocked_client):
    mocked_client.return_value.get_judgment_xml.return_value = b"<judgment></judgment>"
    response = TestClient(app).request("GET", "/judgment/uri", auth=("user", "pass"))
    mocked_client.return_value.get_judgment_xml.assert_called_with("uri")
    assert response.status_code == 200
    assert "<judgment>" in response.text


@patch("openapi_server.apis.reading_api.client_for_basic_auth")
def test_get_not_found(mocked_client):
    mocked_client.return_value.get_judgment_xml.side_effect = Mock(
        side_effect=MarklogicResourceNotFoundError()
    )
    response = TestClient(app).request(
        "GET", "/judgment/bad_uri", auth=("user", "pass")
    )
    mocked_client.return_value.get_judgment_xml.assert_called_with("bad_uri")
    assert response.status_code == 404
    assert "Resource not found." in response.text


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
