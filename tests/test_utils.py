from unittest.mock import Mock

import pytest
from caselawclient.Client import (
    MarklogicUnauthorizedError,
    MarklogicValidationFailedError,
)
from fastapi.exceptions import HTTPException
from openapi_server.apis.utils import error_handling


def test_error_handling_no_exception():
    def example():
        with error_handling():
            return 4

    assert example() == 4


def test_error_handling_python_error(caplog):
    """
    Given you will get a standard Python exception
    When using error_handling
    Then the error response:
      contains a very generic error with no contents
      has a relevant status code
    And outputs the message and traceback to the logs
    """

    def example():
        with error_handling():
            1 / 0

    with pytest.raises(HTTPException) as ex:
        example()
    assert ex.value.detail == "An unknown error occurred outside of Marklogic."
    assert ex.value.status_code == 500
    assert "division by zero" in caplog.text
    assert "1 / 0" in caplog.text


def test_validation_error(caplog):
    """
    Given you will get a validation MarklogicAPIError exception
    When using error_handling
    Then the error response:
      contains the marklogic error message
      is the default message
      has a relevant status code
    And outputs the message to the logs
    """

    def example():
        e = MarklogicValidationFailedError("error_msg")
        e.response = Mock()
        e.response.content = b'<error-response xmlns="http://marklogic.com/xdmp/error"><message>a message from marklogic</message></error-response>'

        with error_handling():
            raise e

    with pytest.raises(HTTPException) as ex:
        example()

    assert ex.value.detail == "a message from marklogic"
    assert ex.value.status_code == 422
    assert "error_msg" in caplog.text


def test_non_validation_error(caplog):
    """
    Given you will get a non-validation MarklogicAPIError exception
    When using error_handling
    Then the error response:
      does not contain the marklogic error message
      is the default message
      has a relevant status code
    And outputs the message to the logs
    """

    def example():
        e = MarklogicUnauthorizedError("error_msg")
        e.response = Mock()
        e.response.content = b'<error-response xmlns="http://marklogic.com/xdmp/error"><message>a message from marklogic</message></error-response>'

        with error_handling():
            raise e

    with pytest.raises(HTTPException) as ex:
        example()

    assert "a message from marklogic" not in ex.value.detail
    assert "Your credentials are not valid" in ex.value.detail
    assert ex.value.status_code == 401
    assert "error_msg" in caplog.text
