# coding: utf-8

from typing import Dict, List  # noqa: F401
from openapi_server.connect import client_for_basic_auth

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

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

router = APIRouter()


@router.get(
    "/judgment/{judgmentUri:path}/lock",
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
) -> None:
    client = client_for_basic_auth(token_basic)
    raise NotImplementedError


@router.put(
    "/judgment/{judgmentUri:path}/lock",
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
) -> None:
    """Locks edit access for a document for the current client. Returns the latest version of the locked document, along with the new lock state."""
    client = client_for_basic_auth(token_basic)
    response = client.checkout_judgment(judgment_uri=judgmentUri, annotation="Locked by API")
    print(response)
    return "OK"



@router.patch(
    "/judgment/{judgmentUri:path}/metadata",
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
