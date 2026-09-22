import pytest
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from backend.app import auth

def credentials():
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

def test_missing_token_is_rejected():
    with pytest.raises(HTTPException) as error:
        auth.get_current_user(None)

    assert error.value.status_code == 401

def test_invalid_token_is_rejected(monkeypatch):
    def reject_token(token):
        raise jwt.InvalidTokenError()

    monkeypatch.setattr(auth.jwks_client, "get_signing_key_from_jwt", reject_token)

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(credentials())

    assert error.value.status_code == 401

def test_expired_token_is_rejected(monkeypatch):
    class SigningKey:
        key = "key"
        algorithm_name = "RS256"

    monkeypatch.setattr(auth.jwks_client, "get_signing_key_from_jwt", lambda token: SigningKey())

    def reject_expired(*args, **kwargs):
        raise jwt.ExpiredSignatureError()

    monkeypatch.setattr(auth.jwt, "decode", reject_expired)

    with pytest.raises(HTTPException) as error:
        auth.get_current_user(credentials())

    assert error.value.status_code == 401

def test_valid_token_returns_authenticated_user(monkeypatch):
    class SigningKey:
        key = "key"
        algorithm_name = "RS256"

    monkeypatch.setattr(auth.jwks_client, "get_signing_key_from_jwt", lambda token: SigningKey())
    monkeypatch.setattr(
        auth.jwt,
        "decode",
        lambda *args, **kwargs: {"sub": "user-id", "email": "user@example.com"},
    )

    user = auth.get_current_user(credentials())

    assert user.id == "user-id"
    assert user.email == "user@example.com"
