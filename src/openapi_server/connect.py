import os

import environ
from caselawclient.Client import DEFAULT_USER_AGENT, MarklogicApiClient
from fastapi import Security

from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_basic

environ.Env.read_env("../.env")  # TODO this is hideous
MARKLOGIC_HOST = os.environ["MARKLOGIC_API_CLIENT_HOST"]
SECURITY_TOKEN_MODEL = Security(get_token_basic)


def client_for_basic_auth(
    token_basic: TokenModel = SECURITY_TOKEN_MODEL,
) -> MarklogicApiClient:
    return MarklogicApiClient(
        host=MARKLOGIC_HOST,
        username=token_basic.username,
        password=token_basic.password,
        use_https=False,
        user_agent=f"ds-caselaw-privileged-api/unknown {DEFAULT_USER_AGENT}",
    )
