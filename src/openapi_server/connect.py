import environ
import os
from fastapi import Security
from openapi_server.security_api import get_token_basic
from openapi_server.models.extra_models import TokenModel  # noqa: F401

environ.Env.read_env("../.env") # TODO this is hideous
MARKLOGIC_HOST = os.environ.get('MARKLOGIC_HOST')

from caselawclient.Client import MarklogicApiClient


def client_for_basic_auth(token_basic: TokenModel = Security(get_token_basic),):
    breakpoint()
    print("Actual Client")
    return MarklogicApiClient(
      host=MARKLOGIC_HOST,
      username=token_basic.username,
      password=token_basic.password,
      use_https=False,
    )
