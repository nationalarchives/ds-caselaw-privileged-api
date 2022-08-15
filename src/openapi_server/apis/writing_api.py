# coding: utf-8

from typing import Dict, List  # noqa: F401
from openapi_server.connect import client_for_basic_auth
from caselawclient.Client import (
    MarklogicResourceLockedError,
    MarklogicResourceUnmanagedError,
)

import requests
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
)
from fastapi.responses import JSONResponse

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

from caselawclient.Client import api_client, MarklogicResourceLockedError, MarklogicResourceUnmanagedError

router = APIRouter()


@router.get(
    "/lock/{judgmentUri:path}",
    responses={
        204: {"description": "Lock state included in header"},
    },
    tags=["Writing"],
    summary="Query lock status for a document",
    response_model_by_alias=True,
)
async def judgment_uri_lock_get(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> requests.Response:
    client = client_for_basic_auth(token_basic)
    try:
        message = client.get_judgment_checkout_status_message(judgmentUri)
        content = { "message": message }
    except MarklogicResourceUnmanagedError as e:
        content = { "message": f"Unable to find judgment, {e}" }
    headers = {"X-Cat-Dog": "alone in the world", "Content-Language": "en-US"}
    return JSONResponse(content=content, headers=headers)


@router.put(
    "/lock/{judgmentUri:path}",
    responses={
        201: {"description": "A single judgment document, in Akoma Ntoso XML"},
        403: {"description": "The document was already locked by another client"},
    },
    tags=["Writing"],
    summary="Lock access to a document",
    response_model_by_alias=True,
)
async def judgment_uri_lock_put(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
):
    """Locks edit access for a document for the current client. Returns the latest version of the locked document, along with the new lock state."""
    client = client_for_basic_auth(token_basic)
    annotation = f"Judgment locked for editing by {token_basic.username}"
    try:
        response = client.checkout_judgment(judgmentUri, annotation)
        judgment = api_client.get_judgment_xml(judgmentUri)
    except (MarklogicResourceLockedError, MarklogicResourceUnmanagedError) as e:
        return f"Failed to lock judgment, {e}"
    print(response.content)
    return "OK"


@router.patch(
    "/metadata/{judgmentUri:path}",
    responses={
        200: {"description": "OK"},
    },
    tags=["Writing"],
    summary="Set document properties",
    response_model_by_alias=True,
)
async def judgment_uri_metadata_patch(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> None:
    ...


@router.put(
    "/judgment/{judgmentUri:path}",
    responses={
        204: {"description": "The document was updated successfully and any client lock released"},
        400: {"description": "The request was malformed, and the document was not modified"},
        412: {"description": "The document was not updated, as it has changed since the version number specified If-Match. To avoid this, the client should lock the document before making any changes to it."},
    },
    tags=["Writing"],
    summary="Update a judgment",
    response_model_by_alias=True,
)
async def judgment_uri_put(
    judgmentUri: str = Path(None, description=""),
    if_match: str = Header(None, description="The last known version number of the document"),
    token_basic: TokenModel = Security(
        get_token_basic
    ),
) -> None:
    """Write a complete new version of the document to the database, and release any client lock."""
    ...
