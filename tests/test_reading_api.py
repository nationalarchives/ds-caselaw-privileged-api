# coding: utf-8
from unittest.mock import patch, Mock

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

@patch("openapi_server.apis.reading_api.client_for_basic_auth")
def test_get_list_unpublished_bad_auth(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = False
    response = TestClient(app).request(
        "GET", "/list/unpublished", auth=("user", "pass")
    )
    assert response.status_code == 403
    assert "Not allowed" in response.text


@patch("openapi_server.apis.reading_api.client_for_basic_auth")
def test_get_list_unpublished(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = True
    advanced_search = mocked_client.return_value.advanced_search.return_value
    advanced_search.text = "true"
    advanced_search.headers = {
        "content-type": "multipart/mixed; boundary=6bfe89fc4493c0e3"
    }
    advanced_search.content = b'\r\n--6bfe89fc4493c0e3\r\nContent-Type: application/xml\r\nX-Primitive: element()\r\nX-Path: /*:response\r\n\r\n<search:response snippet-format="empty-snippet" total="32" start="1" page-length="10" selected="include" xmlns:search="http://marklogic.com/appservices/search">\n  <search:result index="1" uri="/ewhc/scco/2022/1775.xml" path="fn:doc(&quot;/ewhc/scco/2022/1775.xml&quot;)" score="0" confidence="0" fitness="0">\n    <search:snippet/>\n    <search:extracted kind="element"><FRBRdate date="2022-06-30" name="judgment" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"/><FRBRname value="REGINA v NOT REAL NAME" xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0"/><uk:cite xmlns:uk="https://caselaw.nationalarchives.gov.uk/akn">[2000] EWHC 1</uk:cite></search:extracted>\n  </search:result></search:response>'  # noqa: E501

    response = TestClient(app).request(
        "GET", "/list/unpublished", auth=("user", "pass")
    )
    mocked_client.return_value.advanced_search.assert_called_with(
        page=1,
        show_unpublished=True,
        only_unpublished=True,
    )
    assert response.status_code == 200
    assert "ok" in response.text
    judgment = response.json()["data"][0]
    assert judgment["name"] == "REGINA v NOT REAL NAME"
    assert judgment["neutral"] == "[2000] EWHC 1"
    assert judgment["date"] == "2022-06-30"
    assert judgment["uri"] == "/ewhc/scco/2022/1775"
    assert judgment["raw_uri"] == "/ewhc/scco/2022/1775.xml"


@patch("openapi_server.apis.reading_api.client_for_basic_auth")
def test_get_list_unpublished_xml(mocked_client):
    mocked_client.return_value.user_can_view_unpublished_judgments.return_value = True
    advanced_search = mocked_client.return_value.advanced_search.return_value
    advanced_search.text = "true"
    advanced_search.headers = {
        "content-type": "multipart/mixed; boundary=6bfe89fc4493c0e3"
    }
    advanced_search.content = b"\r\n--6bfe89fc4493c0e3\r\nContent-Type: application/xml\r\nX-Primitive: element()\r\nX-Path: /*:response\r\n\r\n<whatever></whatever>"  # noqa: E501

    response = TestClient(app).request(
        "GET",
        "/list/unpublished?page=6",
        auth=("user", "pass"),
        headers={"Content-Type": "application/xml"},
    )
    mocked_client.return_value.advanced_search.assert_called_with(
        page=6,
        show_unpublished=True,
        only_unpublished=True,
    )
    assert response.status_code == 200
    assert "whatever" in response.text
    assert "application/xml" == response.headers.get("Content-Type")
