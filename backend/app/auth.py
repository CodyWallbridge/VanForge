import os
from pathlib import Path
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

jwks_url = os.getenv("NEON_AUTH_JWKS_URL")

if not jwks_url:
    raise RuntimeError("NEON_AUTH_JWKS_URL is not set")

bearer_scheme = HTTPBearer(auto_error=False)
jwks_client = PyJWKClient(jwks_url)

class AuthenticatedUser(BaseModel):
    id: str
    email: str | None = None

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication is required")

    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=[signing_key.algorithm_name],
            options={"verify_aud": False},
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

    user_id = claims.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication token has no user identifier")

    return AuthenticatedUser(id=user_id, email=claims.get("email"))