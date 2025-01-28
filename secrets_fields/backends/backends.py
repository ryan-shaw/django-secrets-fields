from typing import Any
class BaseSecretsBackend:
    def get_ciphertext(self, secret_value: str) -> str:
        """Get ciphertext from backend

        Args:
            secret_value (str): plaintext secret
        """
        raise NotImplementedError()

    def create_secret(self, *args : Any) -> str:
        """Create secret using the backend"""
        raise NotImplementedError()

    def get_secret(self, secret_name: str) -> str:
        raise NotImplementedError()
