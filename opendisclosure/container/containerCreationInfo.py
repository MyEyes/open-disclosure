from os import urandom
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .containerException import ContainerException
from pgpy import PGPKey

class ContainerCreationInfo:
    def __init__(self, pubKey, hashAlgo="sha256") -> None:
        if type(pubKey) is PGPKey:
            self.authorPubKey = pubKey
        else:
            raise ContainerException("Public key is required to create container info")

        self.sharedKey = AESGCM.generate_key(bit_length=256)

        #NOT: On the fence about wether this is a good idea or not
        #     Probably should do some cost benefit analysis
        self.challenge = None

        self.nonce = urandom(12)
        self.meta = {
            'version': "0.3",
            'hashAlgo': hashAlgo,
            'cipher': 'AES256-GCM',
            'nonce': self.nonce
        }
        