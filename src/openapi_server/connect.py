import os

import environ
from caselawclient.Client import DEFAULT_USER_AGENT, MarklogicApiClient
from fastapi import Security
from fastapi.security import HTTPBasicCredentials

from openapi_server.security_api import get_basic_credentials

environ.Env.read_env("../.env")
MARKLOGIC_HOST = os.environ["MARKLOGIC_API_CLIENT_HOST"]
SECURITY_BASIC_CREDENTIALS = Security(get_basic_credentials)


def client_for_basic_auth(
    basic_credentials: HTTPBasicCredentials = SECURITY_BASIC_CREDENTIALS,
) -> MarklogicApiClient:
    return MarklogicApiClient(
        host=MARKLOGIC_HOST,
        username=basic_credentials.username,
        password=basic_credentials.password,
        use_https=False,
        user_agent=f"ds-caselaw-privileged-api/unknown {DEFAULT_USER_AGENT}",
    )
