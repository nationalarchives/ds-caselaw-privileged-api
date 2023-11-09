import os

import environ
from caselawclient.Client import MarklogicApiClient

from fastapi import Security
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

environ.Env.read_env("../.env")  # TODO this is hideous
MARKLOGIC_HOST = os.environ["MARKLOGIC_API_CLIENT_HOST"]


def client_for_basic_auth(
    token_basic: TokenModel = Security(get_token_basic),
):
    return MarklogicApiClient(
        host=MARKLOGIC_HOST,
        username=token_basic.username,
        password=token_basic.password,
        use_https=False,
    )
