from caselawclient.client_helpers import VersionAnnotation, VersionType
from caselawclient.models.documents import DocumentURIString
from fastapi import (
    APIRouter,
    Request,
    Response,
    Security,
)

from openapi_server.connect import client_for_basic_auth
from openapi_server.models.extra_models import TokenModel
from openapi_server.security_api import get_token_basic

from .utils import error_handling

SECURITY_TOKEN_MODEL = Security(get_token_basic)

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
    judgmentUri: str,
    token_basic: TokenModel = SECURITY_TOKEN_MODEL,
):
    client = client_for_basic_auth(token_basic)
    with error_handling():
        message = client.get_judgment_checkout_status_message(DocumentURIString(judgmentUri))
        if message is None:
            response.status_code = 200
            response.headers["X-Locked"] = "0"
            return {"status": "Not locked"}
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
    judgmentUri: str,
    token_basic: TokenModel = SECURITY_TOKEN_MODEL,
    expires="0",
):
    """Locks edit access for a document for the current client. Returns the latest
    version of the locked document, along with the new lock state."""
    client = client_for_basic_auth(token_basic)
    annotation = f"Judgment locked for editing by {token_basic.username}"
    expires = bool(
        int(expires),
    )  # If expires is True then the lock will expire at midnight, otherwise the lock is permanent
    with error_handling():
        _ml_response = client.checkout_judgment(
            DocumentURIString(judgmentUri),
            annotation,
            expires,
        )
        judgment = client.get_judgment_xml(DocumentURIString(judgmentUri), show_unpublished=True)
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
    judgmentUri: str,
    token_basic: TokenModel = SECURITY_TOKEN_MODEL,
):
    client = client_for_basic_auth(token_basic)

    with error_handling():
        client.checkin_judgment(judgment_uri=DocumentURIString(judgmentUri))

    response.status_code = 200
    return {"status": "unlocked"}


@router.patch(
    "/judgment/{judgmentUri:path}",
    responses={
        200: {
            "description": "The document was updated successfully and the lock released if `unlock` is true",
        },
        400: {
            "description": "The request was malformed, and the document was not modified",
        },
    },
    tags=["Writing"],
    summary="Update a judgment",
    response_model_by_alias=True,
)
async def judgment_uri_patch(  # noqa: PLR0913
    request: Request,
    response: Response,
    judgmentUri: str,
    annotation: str = "",
    token_basic: TokenModel = SECURITY_TOKEN_MODEL,
    unlock: bool = False,
) -> dict[str, str]:
    """Write a complete new version of the document to the database,
    and release any client lock."""

    client = client_for_basic_auth(token_basic)
    bytes_body = await request.body()

    rich_annotation = VersionAnnotation(
        version_type=VersionType.ENRICHMENT,
        automated=True,
        message=annotation if annotation else None,
    )

    try:
        with error_handling():
            client.save_locked_judgment_xml(
                judgment_uri=DocumentURIString(judgmentUri),
                judgment_xml=bytes_body,
                annotation=rich_annotation,
            )
    except Exception:
        if unlock:
            with error_handling():
                _ml_response = client.checkin_judgment(judgment_uri=DocumentURIString(judgmentUri))
        raise

    if not unlock:
        response.status_code = 200
        return {"status": "Uploaded (not unlocked)."}

    with error_handling():
        _ml_response = client.checkin_judgment(judgment_uri=DocumentURIString(judgmentUri))

    response.status_code = 200
    return {"status": "Uploaded and unlocked."}
