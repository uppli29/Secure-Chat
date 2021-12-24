from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class AESCipher:

    def __init__(self, key):
        '''The AES class takes in key and initialize the cipher methods'''

        self.key = key

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_ECB)
        # cipherText, tag = cipher.encrypt_and_digest(raw)
        cipherText = cipher.encrypt(pad(raw, AES.block_size))
        return cipherText

    def decrypt(self, enc):
        cipher = AES.new(self.key, AES.MODE_ECB)
        plainText = unpad(cipher.decrypt(enc), AES.block_size)
        return plainText
