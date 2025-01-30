

class BaseSecretsBackend:
    def __init__(self, config : dict):
        self.config = config

    def encrypt(self, plaintext: str) -> str:
        """Encrypt the secret value using the backend"""
        raise NotImplementedError()

    def decrypt(self, ciphertext: str) -> str:
        """Get plain text from the backend

        Args:
            ciphertext (str): ciphertext

        Returns:
            str: plaintext
        """
        raise NotImplementedError()
