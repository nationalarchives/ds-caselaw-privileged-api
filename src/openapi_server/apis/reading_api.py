# coding: utf-8

from typing import Dict, List  # noqa: F401

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
    "/judgment/{judgmentUri:path}",
    responses={
        200: {"description": "A single judgment document, in Akoma Ntoso XML"},
    },
    tags=["Reading"],
    summary="Read a judgment or decision, given its URI",
    response_model_by_alias=True,
)
async def get_document_by_uri(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
) -> None:
    """Unless the client has &#x60;read_unpublished_documents&#x60; permission, then only published documents are accessible."""
    return "jqqzdwd"


@router.get(
    "/metadata/{judgmentUri:path}",
    responses={
        200: {"description": "OK"},
    },
    tags=["Reading"],
    summary="Gets the document&#39;s metadata",
    response_model_by_alias=True,
)
async def judgment_uri_metadata_get(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
) -> None:
    """Unless the client has &#x60;read_unpublished_documents&#x60; permission, then only metadata for published documents are accessible."""
    ...
