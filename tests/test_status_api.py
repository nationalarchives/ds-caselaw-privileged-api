# coding: utf-8

from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from openapi_server.main import app
from caselawclient.Client import MarklogicUnauthorizedError


def test_get_status_no_auth():
    response = TestClient(app).request("GET", "/status", auth=("", ""))
    assert response.status_code == 200


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_no_user(mocked_client=None):
    mocked_client.return_value.user_can_view_unpublished_judgments.side_effect = Mock(
        side_effect=MarklogicUnauthorizedError()
    )
    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 401
    assert response.content == b'{"detail":"/status: user Unauthorised"}'
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user"
    )
    # TODO: This will break when only_published becomes silently false.


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_authorised(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = True

    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 200
    assert response.content == b'"/status: user Authorised"'
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user"
    )


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_less_authorised(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = False

    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 200
    assert response.content == b'"/status: user Authorised"'
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user"
    )
