#AES加密工具
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import os

AES_KEY = os.getenv(
    "AES_SECRET_KEY", 
    b'\x1f\x9b\x0c\x8a\x7d\x6e\x5f\x4a\x3b\x2c\x1d\x0e\xfa\xeb\xdc\xba'
    b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'  # 共32字节
    )
class AESCrypto:
    def __init__(self, key=AES_KEY):
        self.key = key
        self.block_size = AES.block_size

    def encrypt(self, data):
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(data.encode('utf-8'), self.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    def decrypt(self, encrypted_data):
        data = base64.b64decode(encrypted_data)
        iv = data[:self.block_size]
        cipher_text = data[self.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(cipher_text), self.block_size)
        return decrypted.decode('utf-8')

# 实例化，方便全局使用
crypto = AESCrypto() 