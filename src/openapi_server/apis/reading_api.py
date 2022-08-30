# coding: utf-8

from typing import Dict, List  # noqa: F401

from caselawclient.Client import MarklogicAPIError
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

from openapi_server.connect import client_for_basic_auth

router = APIRouter()


@router.get(
    "/judgment/{judgmentUri:path}",
    responses={
        200: {"description": "A single judgment document, in Akoma Ntoso XML"},
        404: {"description": "Document not found"},
    },
    tags=["Reading"],
    summary="Read a judgment or decision, given its URI",
    response_model_by_alias=True,
)
async def get_document_by_uri(
    response: Response,
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
):
    try:
        client = client_for_basic_auth(token_basic)
        judgment = client.get_judgment_xml(judgmentUri)
    except MarklogicAPIError:
        response.status_code = 404
        return "Resource not found."
    return Response(status_code=200, content=judgment, media_type="application/xml")


@router.get(
    "/metadata/{judgmentUri:path}",
    responses={
        200: {"description": "OK"},
    },
    tags=["Reading"],
    summary="Gets the document's metadata",
    response_model_by_alias=True,
)
async def judgment_uri_metadata_get(
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
) -> None:
    """Unless the client has `read_unpublished_documents` permission,
    then only metadata for published documents are accessible."""
    ...
