from fastapi import HTTPException
from contextlib import contextmanager


@contextmanager
def error_handling():
    try:
        yield

    except BaseException as e:
        print(f"EXCEPTION {e}")
        return error_response(e)


def error_response(e):
    """provide a uniform error Response"""

    print("???")
    print(e)
    # If the Exception one about validation, output the entire failure message, otherwise don't.
    raise HTTPException(status_code=e.status_code, detail=e.default_message)
