from .containerException import ContainerException
from pgpy import PGPMessage, PGPKey

#NOT: consider renaming to ContainerAuthorizationTuple
class ContainerKeyPair:
    def __init__(self, pubKey, encSharedKey = None, sharedKey=None) -> None:
        if type(pubKey) is PGPKey:
            self.pub = pubKey
        else:
            raise ContainerException("Pub Key is required")

        if encSharedKey is not None:
            self.encShared = encSharedKey
        elif sharedKey is not None:
            msg = PGPMessage.new(sharedKey)
            self.encShared = bytes(self.pub.encrypt(msg))
        else:
            raise ContainerException("Shared Key is required")

class ContainerAuthorization:
    def __init__(self, authorKey, extraKeys = None) -> None:
        if authorKey is None:
            raise ContainerException("Author Key is required")
        if type(authorKey) is ContainerKeyPair:
            self.authorKey = authorKey
        else:
            raise ContainerException("Author Key is wrong type: {}".format(type(authorKey)))
        if extraKeys is None:
            self.extraKeys = []
        else:
            self.extraKeys = extraKeys

    def authorize(self, pubKey, sharedKey):
        self.extraKeys.append(ContainerKeyPair(pubKey, sharedKey=sharedKey))

    def getKeyById(self,id):
        if id < 0:
            raise ContainerException("Invalid key id")
        elif id == 0:
            return self.authorKey
        elif id <= len(self.extraKeys):
            return self.extraKeys[id-1]

    def getIdOfKey(self, key):
        if self.authorKey.pub.fingerprint == key.fingerprint:
            return 0
        for i in range(len(self.extraKeys)):
            if self.extraKeys[i].pub.fingerprint == key.fingerprint:
                return i+1
        raise ContainerException("Key not in authorization: {}".format(key.fingerprint))

    def getSharedKey(self, privKey):
        if self.authorKey.pub.fingerprint == privKey.fingerprint:
            return privKey.decrypt(PGPMessage.from_blob(self.authorKey.encShared)).message
        for keypair in self.extraKeys:
            if keypair.pub.fingerprint == privKey.fingerprint:
                return privKey.decrypt(PGPMessage.from_blob(keypair.encShared)).message
        raise ContainerException("Couldn't find matching authorization entry for priv key")