# coding: utf-8

import lxml.etree
from typing import Dict, List, Any  # noqa: F401

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
    Request,
    Security,
    status,
)
from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.security_api import get_token_basic

from openapi_server.connect import client_for_basic_auth

from requests_toolbelt.multipart import decoder

router = APIRouter()


def decode_multipart_response(response):
    multipart_data = decoder.MultipartDecoder.from_response(response)
    return multipart_data.parts[0].text


def unpack_list(xpath_list):
    # XPath expressions are often lists; often they should only have one value, or none.
    # Break if there are multiple values, or unpack the list.
    assert (
        len(xpath_list) <= 1
    ), f"There should only be one response, but there were {len(xpath_list)}: \n {xpath_list}"
    if xpath_list:
        return xpath_list[0]
    else:
        return None


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
    "/list/unpublished",
    responses={
        200: {"description": "A list of URLs of unpublished documents in JSON format"},
    },
    tags=["Reading"],
    summary="Get a list of unpublished URLs",
    response_model_by_alias=True,
)
async def list_unpublished_get_get(
    request: Request,
    response: Response,
    token_basic: TokenModel = Security(get_token_basic),
    page: int = 1,  # should not be 0
) -> Any:
    """Unless the client has `read_unpublished_documents` permission,
    then only metadata for published documents are accessible."""
    client = client_for_basic_auth(token_basic)
    if not client.user_can_view_unpublished_judgments(token_basic.username):
        response.status_code = 403
        return {"status": "Not allowed to see unpublished documents"}

    response = client.advanced_search(
        page=page,
        show_unpublished=True,
        only_unpublished=True,
    )

    xml = decode_multipart_response(response)

    content_type = request.headers.get("Content-Type") or ""
    if "application/xml" in content_type:
        return Response(status_code=200, content=xml, media_type="application/xml")

    root = lxml.etree.fromstring(xml)
    namespaces = {
        "search": "http://marklogic.com/appservices/search",
        "uk": "https://caselaw.nationalarchives.gov.uk/akn",
        "akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0",
    }

    results = []

    for result in root.xpath("//search:result", namespaces=namespaces):
        data = {}
        data["raw_uri"] = unpack_list(result.xpath("./@uri"))
        data["uri"] = data["raw_uri"].partition(".xml")[0]
        data["date"] = unpack_list(
            result.xpath(
                ".//akn:FRBRdate[@name='judgment']/@date", namespaces=namespaces
            )
        )
        data["name"] = unpack_list(
            result.xpath(".//akn:FRBRname/@value", namespaces=namespaces)
        )
        data["neutral"] = unpack_list(
            result.xpath(".//uk:cite/text()", namespaces=namespaces)
        )
        results.append(data)

    return {"status": "ok", "data": results}
