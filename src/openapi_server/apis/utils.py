from fastapi import HTTPException
from contextlib import contextmanager
from caselawclient.Client import MarklogicValidationFailedError
import lxml.etree


@contextmanager
def error_handling():
    try:
        yield

    except Exception as e:
        print(f"EXCEPTION {e}")
        return error_response(e)


def error_response(e):
    """provide a uniform error Response"""

    if isinstance(e, MarklogicValidationFailedError):
        root = lxml.etree.fromstring(e.response.content)
        error_message = root.xpath(
            "//mlerror:message/text()",
            namespaces={"mlerror": "http://marklogic.com/xdmp/error"},
        )[0]
    else:
        error_message = e.default_message

    print(e)
    # If the Exception one about validation, output the entire failure message, otherwise don't.
    raise HTTPException(status_code=e.status_code, detail=error_message)
