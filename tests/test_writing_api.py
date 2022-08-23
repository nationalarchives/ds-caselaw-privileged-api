# coding: utf-8

from fastapi.testclient import TestClient
from openapi_server.main import app
from unittest.mock import patch, Mock
from caselawclient.Client import (
    MarklogicUnauthorizedError,
    MarklogicResourceLockedError,
    MarklogicCheckoutConflictError,
    MarklogicResourceNotCheckedOutError,
)

# Read Lock Status (GET /lock/...)


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_get_lock_no_response(mocked_client):
    mocked_client.return_value.get_judgment_checkout_status_message.return_value = None
    response = TestClient(app).request(
        "GET", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.get_judgment_checkout_status_message.assert_called_with(
        "judgment/uri"
    )
    assert response.status_code == 200
    assert response.headers["X-Locked"] == "0"
    assert "Not locked" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_get_lock_locked(mocked_client):
    mocked_client.return_value.get_judgment_checkout_status_message.return_value = (
        "kitten"
    )
    response = TestClient(app).request(
        "GET", "/lock/judgment/uri", auth=("user", "pass")
    )

    mocked_client.return_value.get_judgment_checkout_status_message.assert_called_with(
        "judgment/uri"
    )
    assert response.status_code == 200
    assert response.headers["X-Locked"] == "1"
    assert response.headers["X-Lock-Annotation"] == "kitten"
    assert "kitten" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_get_lock_unauthorised(mocked_client):
    # More generally testing errors are passed through from the client
    mocked_client.return_value.get_judgment_checkout_status_message.side_effect = Mock(
        side_effect=MarklogicUnauthorizedError()
    )
    response = TestClient(app).request(
        "GET", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.get_judgment_checkout_status_message.assert_called_with(
        "judgment/uri"
    )
    assert response.status_code == 401
    assert "credentials are not valid" in response.text


# Acquire Lock (PUT /lock/...)


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_put_lock_success(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.checkout_judgment.return_value = None
    mocked_client.return_value.get_judgment_xml.return_value = b"<judgment></judgment>"
    response = TestClient(app).request(
        "PUT", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.checkout_judgment.assert_called_with(
        "judgment/uri", "Judgment locked for editing by user", False
    )
    assert response.status_code == 201
    assert "<judgment>" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_put_lock_success_temporary(mocked_client):
    """If expires is passed, the lock will expire"""
    mocked_client.return_value.checkout_judgment.return_value = None
    mocked_client.return_value.get_judgment_xml.return_value = b"<judgment></judgment>"
    response = TestClient(app).request(
        "PUT", "/lock/judgment/uri", auth=("user", "pass"), params={"expires": "1"}
    )
    mocked_client.return_value.checkout_judgment.assert_called_with(
        "judgment/uri", "Judgment locked for editing by user", True
    )
    assert response.status_code == 201
    assert "<judgment>" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_put_lock_failure(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.checkout_judgment.side_effect = Mock(
        side_effect=MarklogicResourceLockedError()
    )
    # mocked_client.return_value.get_judgment_xml.return_value = b'<judgment></judgment>'
    response = TestClient(app).request(
        "PUT", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.checkout_judgment.assert_called_with(
        "judgment/uri", "Judgment locked for editing by user", False
    )
    assert response.status_code == 409
    assert "resource is locked by another user" in response.text


# Remove Lock (DELETE /lock/...)


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_delete_lock_success(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.checkin_judgment.return_value = None
    response = TestClient(app).request(
        "DELETE", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.checkin_judgment.assert_called_with(
        judgment_uri="judgment/uri"
    )
    assert response.status_code == 200
    assert "unlocked" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_delete_lock_failure(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.checkin_judgment.side_effect = Mock(
        side_effect=MarklogicCheckoutConflictError()
    )
    response = TestClient(app).request(
        "DELETE", "/lock/judgment/uri", auth=("user", "pass")
    )
    mocked_client.return_value.checkin_judgment.assert_called_with(
        judgment_uri="judgment/uri"
    )
    assert response.status_code == 409
    assert "checked out by another user" in response.text


# Update Judgment (with lock) (PATCH /judgment/...)


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_update_judgment_annotation_ok(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.save_locked_judgment_xml.return_value = None
    response = TestClient(app).request(
        "PATCH",
        "/judgment/is-a-judgment/uri",
        auth=("user", "pass"),
        data="<judgment></judgment>",
        params={"annotation": "hey"},
    )
    mocked_client.return_value.save_locked_judgment_xml.assert_called_with(
        "is-a-judgment/uri", b"<judgment></judgment>", "hey"
    )
    assert response.status_code == 200
    assert "not unlocked" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_update_judgment_unlock_ok(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.save_locked_judgment_xml.return_value = None
    response = TestClient(app).request(
        "PATCH",
        "/judgment/is-a-judgment/uri",
        auth=("user", "pass"),
        data="<judgment></judgment>",
        params={"unlock": "1"},
    )
    mocked_client.return_value.save_locked_judgment_xml.assert_called_with(
        "is-a-judgment/uri", b"<judgment></judgment>", ""
    )
    assert response.status_code == 200
    assert "Uploaded and unlocked" in response.text


@patch("openapi_server.apis.writing_api.client_for_basic_auth")
def test_update_judgment_fail(mocked_client):
    # Checkout Judgment fails with an error or returns None
    mocked_client.return_value.save_locked_judgment_xml.side_effect = Mock(
        side_effect=MarklogicResourceNotCheckedOutError()
    )
    response = TestClient(app).request(
        "PATCH",
        "/judgment/is-a-judgment/uri",
        auth=("user", "pass"),
        data="<judgment></judgment>",
    )
    mocked_client.return_value.save_locked_judgment_xml.assert_called_with(
        "is-a-judgment/uri", b"<judgment></judgment>", ""
    )
    assert response.status_code == 409
    assert "request needed a checkout first" in response.text
