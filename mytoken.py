import os
from cryptography.fernet import Fernet

# Obsługa klucza i tokena
def load_key():
    if not os.path.exists("token/key.key"):
        key = Fernet.generate_key()
        with open("token/key.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("token/key.key", "rb") as key_file:
            key = key_file.read()
    return key

def encrypt_token(token):
    key = load_key()
    cipher_suite = Fernet(key)
    encrypted_token = cipher_suite.encrypt(token.encode())
    os.makedirs("token", exist_ok=True)  # Tworzymy folder, jeśli go nie ma
    with open("token/encrypted_token.txt", "wb") as token_file:
        token_file.write(encrypted_token)

def get_bot_token():
    key = load_key()
    cipher_suite = Fernet(key)
    with open("token/encrypted_token.txt", "rb") as token_file:
        encrypted_token = token_file.read()
    return cipher_suite.decrypt(encrypted_token).decode()
