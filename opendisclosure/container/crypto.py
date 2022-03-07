from os import urandom
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class CipherWrapper:
    def __init__(self, name, key) -> None:
        self.algo = None
        algName, modeName = name.split("-")
        if algName[0:3] == "AES":
            self.algo = algorithms.AES(key)
        if modeName == "GCM":
            self.mode = modes.GCM

    def GetEncryptor(self):
        return Encryptor(self.algo, self.mode)

    def GetDecryptor(self):
        return Decryptor(self.algo, self.mode)

class Encryptor:
    def __init__(self, algo, mode) -> None:
        self.iv = urandom(12)
        self.cipher = Cipher(algo, mode(self.iv))

    def encrypt(self, data):
        encryptor = self.cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return self.iv+encryptor.tag+ciphertext
        

class Decryptor:
    def __init__(self, algo, mode) -> None:
        self.algo = algo
        self.mode = mode

    def decrypt(self, data):
        iv = data[0:12]
        tag = data[12:28]
        data = data[28:]
        cipher = Cipher(self.algo, self.mode(iv, tag))
        decryptor = cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()