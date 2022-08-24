# coding: utf-8

from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from openapi_server.main import app
from caselawclient.Client import MarklogicUnauthorizedError


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_unauthorised(mocked_client=None):
    mocked_client.return_value.advanced_search.side_effect = Mock(
        side_effect=MarklogicUnauthorizedError()
    )
    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 401
    assert response.content == b'{"detail":"/status: user Unauthorised"}'
    mocked_client.return_value.advanced_search.assert_called_with(only_unpublished=True)
    # TODO: This will break when only_published becomes silently false.


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_authorised(mocked_client):
    mocked_client.return_value.advanced_search.return_value = "Not an error"

    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 200
    assert response.content == b'"/status: user Authorised"'
    mocked_client.return_value.advanced_search.assert_called_with(only_unpublished=True)
