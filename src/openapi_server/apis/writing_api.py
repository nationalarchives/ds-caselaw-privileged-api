# coding: utf-8

from typing import Dict, List, Optional  # noqa: F401

from caselawclient.Client import MarklogicAPIError

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Request,
    Path,
    Query,
    Response,
    Security,
    status,
)
from openapi_server.connect import client_for_basic_auth
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_basic

router = APIRouter()


@router.get(
    "/lock/{judgmentUri:path}",
    responses={
        200: {
            "description": "Lock state included in X-Locked header; annotation in X-Lock-Annotation header.",
            "headers": {
                "X-Locked": {
                    "description": "Is the document locked?",
                    "schema": {"type": "boolean string", "format": "0|1"},
                },
                "X-Lock-Annotation": {
                    "description": """If locked, the message left when the document was locked.
                    Usually contains who has locked it""",
                    "schema": {"type": "string"},
                },
            },
        },
    },
    tags=["Writing"],
    summary="Query lock status for a document",
    response_model_by_alias=True,
)
async def judgment_uri_lock_get(
    response: Response,
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
):
    client = client_for_basic_auth(token_basic)
    try:
        message = client.get_judgment_checkout_status_message(judgmentUri)
        if message is None:
            response.status_code = 200
            response.headers["X-Locked"] = "0"
            return {"status": "Not locked"}
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)
    response.status_code = 200
    response.headers["X-Lock-Annotation"] = message
    response.headers["X-Locked"] = "1"
    return {"status": "Locked", "annotation": message}


@router.put(
    "/lock/{judgmentUri:path}",
    status_code=201,
    responses={
        201: {
            "description": "The lock has been created. Returns the locked judgment's Akoma Ntoso XML",
            "content": {"application/akn+xml ": {}},
        },
        409: {"description": "The document was already locked by another client"},
    },
    tags=["Writing"],
    summary="Lock access to a document",
    response_model_by_alias=True,
)
async def judgment_uri_lock_put(
    response: Response,
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
    expires="0",
):
    """Locks edit access for a document for the current client. Returns the latest
    version of the locked document, along with the new lock state."""
    client = client_for_basic_auth(token_basic)
    annotation = f"Judgment locked for editing by {token_basic.username}"
    expires = bool(
        int(expires)
    )  # If expires is True then the lock will expire at midnight, otherwise the lock is permanent
    try:
        _ml_response = client.checkout_judgment(  # noqa: F841
            judgmentUri, annotation, expires
        )
        judgment = client.get_judgment_xml(judgmentUri, show_unpublished=True)
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)
    return Response(status_code=201, content=judgment, media_type="application/xml")


@router.delete(
    "/lock/{judgmentUri:path}",
    responses={
        200: {"description": "Lock removed from judgment"},
        409: {"description": "The document was already locked by different user"},
    },
    tags=["Writing"],
    summary="Unlock access to a document",
    response_model_by_alias=True,
)
async def judgment_uri_lock_delete(
    response: Response,
    judgmentUri: str = Path(None, description=""),
    token_basic: TokenModel = Security(get_token_basic),
):
    client = client_for_basic_auth(token_basic)
    try:
        client.checkin_judgment(judgment_uri=judgmentUri)
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)

    response.status_code = 200
    return "unlocked"


@router.patch(
    "/judgment/{judgmentUri:path}",
    responses={
        200: {
            "description": "The document was updated successfully and the lock released if `unlock` is true"
        },
        400: {
            "description": "The request was malformed, and the document was not modified"
        },
        412: {
            "description": """Not yet implemented: The document was not updated, as it has changed since
            the version number specified If-Match. To avoid this, the client should
            lock the document before making any changes to it."""
        },
    },
    tags=["Writing"],
    summary="Update a judgment",
    response_model_by_alias=True,
)
async def judgment_uri_patch(
    request: Request,
    response: Response,
    judgmentUri: str = Path(None, description=""),
    if_match: str = Header(
        None, description="The last known version number of the document"
    ),
    token_basic: TokenModel = Security(get_token_basic),
    annotation: str = "",
    unlock: bool = False,
) -> str:
    """Write a complete new version of the document to the database,
    and release any client lock."""

    client = client_for_basic_auth(token_basic)
    bytes_body = await request.body()
    try:
        _ml_response = client.save_locked_judgment_xml(  # noqa: F841
            # judgment_uri=judgmentUri,
            # judgment_xml=body,
            # annotation=annotation,
            judgmentUri,
            bytes_body,
            annotation,
        )
    # not idea which of these can occur, copied whcolesale
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)

    if not unlock:
        response.status_code = 200
        return "Uploaded (not unlocked)"

    try:
        _ml_response = client.checkin_judgment(judgment_uri=judgmentUri)  # noqa: F841
    except MarklogicAPIError as e:
        return Response(e.default_message, status_code=e.status_code)

    response.status_code = 200
    return "Uploaded and unlocked."
