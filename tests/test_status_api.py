# coding: utf-8

from fastapi.testclient import TestClient
import unittest
from unittest.mock import MagicMock, patch
import openapi_server
from openapi_server.connect import client_for_basic_auth
import os
from openapi_server.main import app
from caselawclient.Client import MarklogicApiClient
import base64
from unittest import TestCase

def fake_client():
    breakpoint()
    print ("FAKE CLIENT")
    return 4

def test_new(client: TestClient):
    print(client)
    response_text = """
    <dls:checkout xmlns:dls="http://marklogic.com/xdmp/dls">
        <dls:document-uri>/ukpc/2022/17.xml</dls:document-uri>
        <dls:annotation>locked by a kitten</dls:annotation>
        <dls:timeout>0</dls:timeout>
        <dls:timestamp>1660210484</dls:timestamp>
        <sec:user-id xmlns:sec="http://marklogic.com/xdmp/security">10853946559473170020</sec:user-id>
    </dls:checkout>
    """

    with patch.object(MarklogicApiClient, 'eval', return_value=MagicMock(text=response_text)) as mock_method:
        #ml_client = MarklogicApiClient("","","",False)
        #result = ml_client.eval("/ewca/2002/2")
        #assert result == "locked by a kitten"
        headers = {
            "Authorization": "Basic " + base64.b64encode(b"username:password").decode('utf-8'),
        }
        response = client.request(
            "GET",
            "/status",
            headers=headers,
        )
        TestCase().assertEqual(response.text, "Z", headers="Basic 123")
        breakpoint()



# class TestAtomFeed(object):
#     @patch("openapi_server.connect.client_for_basic_auth")
#     def test_status_get(self, mock_server):
#         mock_server.return_value = MagicMock(return_value=fake_client)
#         client = TestClient(app)
#         response = client.get("/")
#         # raise RuntimeError()

#     def test_new_function(self, client: TestClient):
#         response_text = """
#         <dls:checkout xmlns:dls="http://marklogic.com/xdmp/dls">
#             <dls:document-uri>/ukpc/2022/17.xml</dls:document-uri>
#             <dls:annotation>locked by a kitten</dls:annotation>
#             <dls:timeout>0</dls:timeout>
#             <dls:timestamp>1660210484</dls:timestamp>
#             <sec:user-id xmlns:sec="http://marklogic.com/xdmp/security">10853946559473170020</sec:user-id>
#         </dls:checkout>
#         """

#         with patch.object(MarklogicApiClient, 'eval', return_value=MagicMock(text=response_text)) as mock_method:



# #@patch("openapi_server.connect.client_for_basic_auth", MagicMock(return_value=fake_client))
# # @patch("openapi_server.apis.status_api.status_get", MagicMock(return_value=fake_client()))
# # def test_status_get_unauthorised(client: TestClient):
# #     """Test case for status_get

# #     Health check

# #     Checks against the staging marklogic
# #     """
# #     assert openapi_server.apis.status_api.status_get()== 4
# #     headers = {
# #         "Authorization": "Basic " + base64.b64encode(b"username:password").decode('utf-8'),
# #     }
# #     response = client.request(
# #         "GET",
# #         "/status",
# #         headers=headers,
# #     )

# #     assert response.status_code == 401
# #     assert response.content == b'{"detail":"/status: username Unauthorised"}'
