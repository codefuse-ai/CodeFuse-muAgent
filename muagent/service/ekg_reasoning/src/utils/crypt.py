from cryptography.fernet import Fernet


def decrypt(encryped, key):
    f = Fernet(key)
    res_bytes = f.decrypt(encryped)
    res_str = res_bytes.decode('utf-8')
    return res_str

def encrypt(text: str, key):
    f = Fernet(key)
    text_bytes = bytes(text, 'utf-8')
    res_bytes = f.encrypt(text_bytes)
    return res_bytes


