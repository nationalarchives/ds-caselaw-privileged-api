# coding: utf-8

from typing import Dict, List  # noqa: F401

from caselawclient.Client import MarklogicUnauthorizedError, MarklogicAPIError

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
from fastapi.security import HTTPBasicCredentials
from openapi_server.connect import client_for_basic_auth
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

router = APIRouter()


@router.get(
    "/healthcheck",
    responses={
        200: {"description": "The service is available, and we can see Marklogic"},
    },
    tags=["Status"],
    summary="Health check",
    response_model_by_alias=True,
)
async def healthcheck_get() -> str:
    """A test endpoint that checks Marklogic is present"""
    client = client_for_basic_auth(HTTPBasicCredentials(username="", password=""))
    try:
        client.user_can_view_unpublished_judgments("")
    except MarklogicUnauthorizedError:
        pass
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)

    return "/healthcheck: Marklogic OK"


@router.get(
    "/status",
    responses={
        200: {
            "description": """The service is available, and if authentication was provided, the authentication is valid.
            X-Read-Unpublished will be 1 if the user can read unpublished, 0 otherwise"""
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
    response: Response,
    token_basic: TokenModel = Security(get_token_basic),
) -> str:
    """A test endpoint that can be used by clients to verify service availability,
    and to verify valid authentication credentials. Authentication is not required,
    but if it is provided, it will be checked for validity."""
    username = token_basic.username

    if not username:
        return "/status: no username"
    client = client_for_basic_auth(token_basic)
    try:
        view_unpublished = client.user_can_view_unpublished_judgments(username)
    except MarklogicUnauthorizedError:
        raise HTTPException(status_code=401, detail=f"/status: {username} Unauthorised")

    response.headers["X-Read-Unpublished"] = "1" if view_unpublished else "0"

    return f"/status: {username} Authorised, and can{'not' if not view_unpublished else ''} view unpublished judgments"
