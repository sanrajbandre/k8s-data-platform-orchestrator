from app.core.security import create_access_token, decode_token


def test_access_token_roundtrip() -> None:
    token = create_access_token("123")
    claims = decode_token(token, expected_type="access")
    assert claims["sub"] == "123"
