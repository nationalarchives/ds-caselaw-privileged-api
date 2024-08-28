from unittest.mock import Mock, patch

from caselawclient.Client import MarklogicUnauthorizedError
from fastapi.testclient import TestClient

from openapi_server.main import app


def test_get_status_no_auth():
    response = TestClient(app).request("GET", "/status", auth=("", ""))
    assert response.status_code == 200


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_no_such_user(mocked_client=None):
    mocked_client.return_value.user_can_view_unpublished_judgments.side_effect = Mock(
        side_effect=MarklogicUnauthorizedError(),
    )
    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 401
    assert (
        response.content
        == b'{"detail":"Your credentials are not valid, or you did not provide any by basic authentication"}'
    )
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user",
    )


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_authorised(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = True

    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 200
    assert "/status: user Authorised, and can view" in response.text
    assert response.headers["X-Read-Unpublished"] == "1"
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user",
    )


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_get_status_less_authorised(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = False

    response = TestClient(app).request("GET", "/status", auth=("user", "pass"))
    assert response.status_code == 200
    assert "/status: user Authorised, and cannot view" in response.text
    assert response.headers["X-Read-Unpublished"] == "0"
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "user",
    )


@patch("openapi_server.apis.status_api.client_for_basic_auth")
def test_healthcheck(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.side_effect = Mock(
        side_effect=MarklogicUnauthorizedError(),
    )

    response = TestClient(app).request("GET", "/healthcheck")
    assert response.status_code == 200
    assert "/healthcheck: Marklogic OK" in response.text
    mocked_client.return_value.user_can_view_unpublished_judgments.assert_called_with(
        "",
    )
