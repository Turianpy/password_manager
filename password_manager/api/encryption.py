import base64
from os import urandom

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(master_password, salt, iterations=100000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.tobytes(),
        iterations=iterations,
        backend=default_backend()
    )
    key = kdf.derive(master_password.encode())
    return key


def encrypt_password(password, master_password, salt, iterations=100000):
    key = derive_key(master_password, salt, iterations)
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password.encode()) + padder.finalize()
    encrypted_password = encryptor.update(padded_data) + encryptor.finalize()
    return iv, encrypted_password


def decrypt_password(encrypted_password, master_password, salt, iv, iterations=100000):
    key = derive_key(master_password, salt, iterations)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()

    decrypted_padded = decryptor.update(encrypted_password) + decryptor.finalize()
    decrypted_password = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted_password.decode()
