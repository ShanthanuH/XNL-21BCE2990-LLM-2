
import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class EncryptionUtils:
    """Utilities for encryption and decryption of sensitive data"""

    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """Generate a key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(16)

        # Use PBKDF2 to derive a key
        key = hashlib.pbkdf2_hmac(
            'sha256',  # Hash algorithm
            password.encode(),  # Password as bytes
            salt,  # Salt
            100000,  # Number of iterations
            32  # Key length (32 bytes = 256 bits)
        )

        return key, salt

    @staticmethod
    def encrypt_data(data: str, key: bytes) -> bytes:
        """Encrypt data using AES-256-CBC"""
        # Generate a random IV
        iv = os.urandom(16)

        # Create an encryptor
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Pad the data
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Prepend IV to the encrypted data
        return iv + encrypted_data

    @staticmethod
    def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
        """Decrypt data using AES-256-CBC"""
        # Extract IV (first 16 bytes)
        iv = encrypted_data[:16]
        actual_encrypted_data = encrypted_data[16:]

        # Create a decryptor
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt
        decrypted_padded_data = decryptor.update(actual_encrypted_data) + decryptor.finalize()

        # Unpad the data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

        return unpadded_data.decode()

    @staticmethod
    def encrypt_model_weights(model_weights: bytes, password: str) -> dict:
        """Encrypt model weights for secure storage"""
        # Generate key and salt
        salt = os.urandom(16)
        key, _ = EncryptionUtils.generate_key(password, salt)

        # Encrypt the weights
        encrypted_weights = EncryptionUtils.encrypt_data(model_weights.decode('latin1'), key)

        # Base64 encode for storage
        return {
            "salt": base64.b64encode(salt).decode(),
            "encrypted_weights": base64.b64encode(encrypted_weights).decode()
        }

    @staticmethod
    def decrypt_model_weights(encrypted_data: dict, password: str) -> bytes:
        """Decrypt model weights for loading"""
        # Decode salt
        salt = base64.b64decode(encrypted_data["salt"])

        # Generate key
        key, _ = EncryptionUtils.generate_key(password, salt)

        # Decrypt weights
        encrypted_weights = base64.b64decode(encrypted_data["encrypted_weights"])
        decrypted_weights = EncryptionUtils.decrypt_data(encrypted_weights, key)

        return decrypted_weights.encode('latin1')
