from enum import Enum
import time

from .containerException import ContainerException
import hashlib

class ContainerEntryType(Enum):
    TEXT = 1
    FILE = 2
    AUTHORIZE = 3
    RELEASE = 4

class ContainerEntryHashData:
    def __init__(self, prevHashData=None, entry=None, clearHash=None, storedHash=None, clearSig=None, storedSig=None) -> None:
        if entry is not None:
            if prevHashData is None:
                raise ContainerException("Can only construct hash data from entry with previous hash data")
            if entry.IsUnlocked():
                self.clearHash = self.__calcHash(prevHashData.clearHash, entry.getBlob())
            else:
                self.clearHash = None
            self.storedHash = self.__calcHash(prevHashData.storedHash, entry.getStoredBlob())
            self.storedSig = None
            self.clearSig = None
        else:
            if clearHash is None or storedHash is None:
                raise ContainerException("If hashes are given directly both clear and stored hash have to be provided")
            # if prevHashData is None:
            #     if clearHash != storedHash:
            #         raise ContainerException("If prevHashData is None clearHash and storedHash have to be identical")
            self.clearHash = clearHash
            self.storedHash = storedHash
            self.clearSig = clearSig
            self.storedSig = storedSig

    def sign(self, privKey):
        if self.clearHash is None or self.storedHash is None:
            raise ContainerException("Can only sign complete container entry")
        if self.storedSig is not None or self.clearSig is not None:
            raise ContainerException("Hash Data already signed")
        self.clearSig = privKey.sign(self.clearHash)
        self.storedSig = privKey.sign(self.storedHash)

    def verify(self, pubKey):
        if self.clearHash is not None:
            if self.clearSig is None:
                raise ContainerException("Missing clear signature")
            else:
                if not pubKey.verify(self.clearHash, self.clearSig):
                    raise ContainerException("Clear signature invalid")
        if self.storedHash is not None:
            if self.storedSig is None:
                raise ContainerException("Missing stored signature")
            else:
                if not pubKey.verify(self.storedHash, self.storedSig):
                    raise ContainerException("Stored signature invalid")
        return True

    def __calcHash(self, prevHash, data):
        m = hashlib.sha256()
        m.update(data)
        m.update(prevHash)
        return m.digest()

    def matches(self, prevHashData, entry):
        #To check if hashes are correct create temporary instance and check if existing hashes match
        testData = ContainerEntryHashData(prevHashData=prevHashData, entry=entry)
        if testData.clearHash:
            if testData.clearHash != self.clearHash:
                return False
        return testData.storedHash == self.storedHash



class ContainerEntry:
    #TODO: consider adding timestamps
    def __init__(self, entryType, creatorId = -1, title = None, data = None, storedData = None, encrypted = True, hashData = None, timestamp=None, cipher=None) -> None:
        if type(entryType) is ContainerEntryType:
            self.type = entryType
        else:
            raise ContainerException("Invalid container entry type")

        if timestamp is None:
            self.timestamp = int(time.time())
        elif type(timestamp) is int:
            self.timestamp = timestamp
        self.data = data
        self.storedData = storedData
        
        self.encrypted = encrypted
        if self.encrypted:
            if self.type == ContainerEntryType.AUTHORIZE:
                raise ContainerException("AUTHORIZE entry must not be encrypted")
            if self.type == ContainerEntryType.RELEASE:
                raise ContainerException("RELEASE entry must not be encrypted")
            if self.storedData is None:
                if cipher is None:
                    raise ContainerException("Can not create encrypted entry from clear data without cipher")
                encryptor = cipher.GetEncryptor()
                if type(self.data) is bytes:
                    self.storedData = encryptor.encrypt(self.data)
                elif type(self.data) is str:
                    self.storedData = encryptor.encrypt(self.data.encode())
                else:
                    raise ContainerException("Unexpected type of data")

        else: #Not encrypted
            if self.data is not None:
                if self.storedData is None:
                    if type(self.data) is bytes:
                        self.storedData = self.data
                    elif type(self.data) is str:
                        self.storedData = self.data.encode()
                    else:
                        raise ContainerException("Unexpected type of data")
                if self.data != self.storedData:
                    if not type(self.data) is str or self.storedData != self.data.encode():
                        raise ContainerException("data and stored data mismatch")
            else:
                self.data = self.storedData

        self.creatorId = creatorId
        self.title = title

        if self.data is None and self.storedData is None:
            raise ContainerException("Entry must contain data")

        self.hashData = hashData

    def IsUnlocked(self):
        return self.data is not None

    def Unlock(self, cipher):
        if not self.encrypted:
            return
        decryptor = cipher.GetDecryptor()
        self.data = decryptor.decrypt(self.storedData)
        if self.type == ContainerEntryType.TEXT:
            self.data = self.data.decode()

    def createHashData(self, prevHashData):
        if self.hashData is not None:
            raise ContainerException("Hash data already exists")
        self.hashData = ContainerEntryHashData(prevHashData=prevHashData, entry=self)

    def signHashData(self, privKey):
        if self.hashData is None:
            raise ContainerException("Hash data doesn't exist, can't sign")
        if self.hashData.storedSig is not None or self.hashData.clearSig is not None:
            raise ContainerException("Hash data is already signed")
        self.hashData.sign(privKey)

    def getBlob(self):
        if self.data is None:
            raise ContainerException("Data is unavailable")
        blob = b""
        blob += str(self.creatorId).encode()
        if self.title is not None:
            blob += b":"
            blob += self.title.encode()
        blob += b":"
        if type(self.data) is bytes:
            blob += self.data
        elif type(self.data) is str:
            blob += self.data.encode()
        else:
            raise ContainerException("Data is unexpected type: {}".format(type(self.data)))
        return blob

    def getStoredBlob(self):
        if self.storedData is None:
            raise ContainerException("Stored data is unavailable")
        blob = b""
        blob += str(self.creatorId).encode()
        if self.title is not None:
            blob += b":"
            blob += self.title.encode()
        blob += b":"
        if type(self.storedData) is bytes:
            blob += self.storedData
        else:
            raise ContainerException("Stored data is unexpected type: {}".format(type(self.storedData)))
        return blob

        

        