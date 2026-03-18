from pydantic import SecretStr
from utils.signer import create_verification_token, sign_token, verify_signature

from core.settings import SETTINGS


def test_sign_and_verify_token():
    SETTINGS.secret_key = SecretStr("test-secret")

    token = create_verification_token()
    signed = sign_token(token)

    assert signed.startswith(f"{token}.")
    assert verify_signature(signed) == token

    assert verify_signature(token) is None

    tampered = signed[:-1] + ("A" if signed[-1] != "A" else "B")
    assert verify_signature(tampered) is None
