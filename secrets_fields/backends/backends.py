class BaseSecretsBackend:
    def create_secret(self, secret_name: str, secret_value: str):
        """Create secret using the backend

        Args:
            secret_name (str): name of the secret
            secret_value (str): plaintext secret
        """
        raise NotImplementedError()

    def get_secret(self, secret_name: str) -> str:
        raise NotImplementedError()
