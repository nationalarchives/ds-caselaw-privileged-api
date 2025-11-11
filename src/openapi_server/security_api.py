from fastapi import Depends, Security  # noqa: F401
from fastapi.openapi.models import OAuthFlowImplicit, OAuthFlows  # noqa: F401
from fastapi.security import (  # noqa: F401
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from fastapi.security.api_key import (  # noqa: F401
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
)

basic_credentials_auth = Depends(HTTPBasic())


def get_basic_credentials(
    credentials: HTTPBasicCredentials = basic_credentials_auth,
) -> HTTPBasicCredentials:
    """
    Check and retrieve authentication information from basic auth.

    :param credentials Credentials provided by Authorization header
    :type credentials: HTTPBasicCredentials
    :rtype: HTTPBasicCredentials | None
    """
    # we pass the problem upstream -- auth is a MarkLogic problem
    return credentials
