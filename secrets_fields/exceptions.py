class DecryptionException(Exception):
    def __init__(self, cause: Exception):
        self.cause = cause

    def __str__(self) -> str:
        return f"Decryption failed: {str(self.cause)}"
