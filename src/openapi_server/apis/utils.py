from fastapi import HTTPException
from contextlib import contextmanager
from caselawclient.Client import MarklogicValidationFailedError, MarklogicAPIError
import lxml.etree
import traceback


@contextmanager
def error_handling():
    try:
        yield

    except Exception as e:
        print(f"EXCEPTION {e}")
        return error_response(e)


def error_response(e):
    """provide a uniform error Response"""
    print("### Error contents:")
    print(e)
    print("### End of error")

    if isinstance(e, MarklogicValidationFailedError):
        root = lxml.etree.fromstring(e.response.content)
        error_message = root.xpath(
            "//mlerror:message/text()",
            namespaces={"mlerror": "http://marklogic.com/xdmp/error"},
        )[0]
        raise HTTPException(status_code=e.status_code, detail=error_message)
    elif isinstance(e, MarklogicAPIError):
        raise HTTPException(status_code=e.status_code, detail=e.default_message)
    else:
        # presumably a Python error, not a Marklogic one
        print("### Traceback")
        traceback.print_exc()
        print("### End traceback")
        raise HTTPException(
            status_code=500, detail="An unknown error occurred outside of Marklogic."
        )
