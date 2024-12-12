from nacl import secret, utils as nacl_utils
from base64 import b64encode, b64decode
import json
from typing import Union, Dict, Any


class CryptoManager:
    def __init__(self, key: bytes = None):
        """Initialize with an optional key, or generate a new one."""
        self.key = key if key else nacl_utils.random(secret.SecretBox.KEY_SIZE)
        self.box = secret.SecretBox(self.key)

    def encrypt(self, data: Union[str, dict]) -> str:
        """
        Encrypt data and return as base64 string.

        Args:
            data: String or dict to encrypt

        Returns:
            Base64 encoded encrypted data
        """
        if isinstance(data, dict):
            data = json.dumps(data)

        encrypted = self.box.encrypt(data.encode())
        return b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> Union[str, Dict[str, Any]]:
        """
        Decrypt base64 encoded data.

        Args:
            encrypted_data: Base64 encoded encrypted data

        Returns:
            Decrypted data as string or dict if valid JSON
        """
        try:
            decoded = b64decode(encrypted_data.encode())
            decrypted = self.box.decrypt(decoded).decode('utf-8')

            # Try to parse as JSON
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def get_key_b64(self) -> str:
        """Get the encryption key as base64 string."""
        return b64encode(self.key).decode('utf-8')

    @classmethod
    def from_key_b64(cls, key_b64: str) -> 'CryptoManager':
        """Create a CryptoManager instance from a base64 encoded key."""
        key = b64decode(key_b64.encode())
        return cls(key)


def generate_key() -> str:
    """Generate a new random encryption key as base64 string."""
    key = nacl_utils.random(secret.SecretBox.KEY_SIZE)
    return b64encode(key).decode('utf-8')