# coding: utf-8

from typing import Dict, List  # noqa: F401

from caselawclient.Client import MarklogicUnauthorizedError

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)
from openapi_server.connect import client_for_basic_auth
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

router = APIRouter()


@router.get(
    "/status",
    responses={
        200: {
            "description": "The service is available, and if authentication was provided, the authentication is valid."
        },
        401: {
            "description": "The service is available, but the provided authentication was not valid."
        },
    },
    tags=["Status"],
    summary="Health check",
    response_model_by_alias=True,
)
async def status_get(
    token_basic: TokenModel = Security(get_token_basic),
) -> str:
    """A test endpoint that can be used by clients to verify service availability, and to verify valid authentication credentials. Authentication is not required, but if it is provided, it will be checked for validity."""
    client = client_for_basic_auth(token_basic)

    try:
        search_response = client.advanced_search(only_unpublished=True)
    except MarklogicUnauthorizedError:
        raise HTTPException(
            status_code=401, detail="/status: {token_basic.username} Unauthorised"
        )
    return "/status: {token_basic.username} Authorised"
