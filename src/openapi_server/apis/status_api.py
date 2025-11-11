import contextlib

from caselawclient.Client import MarklogicUnauthorizedError
from fastapi import (
    APIRouter,
    Response,
    Security,
)
from fastapi.security import HTTPBasicCredentials

from openapi_server.connect import client_for_basic_auth
from openapi_server.security_api import get_basic_credentials

from .utils import error_handling

SECURITY_BASIC_CREDENTIALS = Security(get_basic_credentials)

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
async def healthcheck_get() -> dict[str, str]:
    """A test endpoint that checks Marklogic is present"""
    client = client_for_basic_auth(HTTPBasicCredentials(username="", password=""))
    with error_handling(), contextlib.suppress(MarklogicUnauthorizedError):
        # MarklogicUnauthorizedError is an expected error
        client.user_can_view_unpublished_judgments("")
    return {"status": "/healthcheck: Marklogic OK"}


@router.get(
    "/status",
    responses={
        200: {
            "description": """The service is available, and if authentication was provided, the authentication is valid.
            X-Read-Unpublished will be 1 if the user can read unpublished, 0 otherwise""",
        },
        401: {
            "description": "The service is available, but the provided authentication was not valid.",
        },
    },
    tags=["Status"],
    summary="Health check",
    response_model_by_alias=True,
)
async def status_get(
    response: Response,
    basic_credentials: HTTPBasicCredentials = SECURITY_BASIC_CREDENTIALS,
) -> dict[str, str]:
    """A test endpoint that can be used by clients to verify service availability,
    and to verify valid authentication credentials. Authentication is not required,
    but if it is provided, it will be checked for validity."""
    username = basic_credentials.username

    if not username:
        return {"status": "/status: no username"}
    client = client_for_basic_auth(basic_credentials)
    with error_handling():
        view_unpublished = client.user_can_view_unpublished_judgments(username)

    response.headers["X-Read-Unpublished"] = "1" if view_unpublished else "0"

    can_cannot = f"can{'not' if not view_unpublished else ''}"

    return {
        "status": f"/status: {username} Authorised, and {can_cannot} view unpublished judgments",
    }
