from django.core.management import call_command
from cryptography.fernet import Fernet
from io import StringIO


def test_generate_fernet_key():
    out = StringIO()
    call_command("generate_fernet_key", stdout=out)
    output = out.getvalue().strip().split("\n")

    assert output[0].startswith("Your Fernet key:")
    key_str = output[0].split(": ")[1]
    key_bytes = key_str.encode("utf-8")
    Fernet(key_bytes)  # This should not raise an error if the key is valid
    assert (
        "Store this key in a safe place, such as your environment variables or a secrets manager."
        in output[1]
    )
