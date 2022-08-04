# coding: utf-8

from typing import Dict, List  # noqa: F401
import os
import environ
environ.Env.read_env("../.env") # TODO this is hideous
MARKLOGIC_HOST = os.environ['MARKLOGIC_HOST']

from caselawclient.Client import MarklogicApiClient, MarklogicUnauthorizedError

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
    HTTPException
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

router = APIRouter()


@router.get(
    "/status",
    responses={
        200: {"description": "The service is available, and if authentication was provided, the authentication is valid."},
        401: {"description": "The service is available, but the provided authentication was not valid."},
    },
    tags=["Status"],
    summary="Health check",
    response_model_by_alias=True,
)
async def status_get(
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> None:
    """A test endpoint that can be used by clients to verify service availability, and to verify valid authentication credentials. Authentication is not required, but if it is provided, it will be checked for validity. """
    client = MarklogicApiClient(
    host=MARKLOGIC_HOST,
    username=token_basic.username,
    password=token_basic.password,
    use_https=False,
    )

    try:
        search_response = client.advanced_search(only_unpublished=True)
    except MarklogicUnauthorizedError:
        raise HTTPException(status_code=401, detail="/status: {token_basic.username} Unauthorised")
    return "/status: {token_basic.username} Authorised"
