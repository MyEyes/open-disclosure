import hashlib
import os
from opendisclosure.container.containerEntry import ContainerEntry, ContainerEntryHashData, ContainerEntryType

from opendisclosure.container.containerException import ContainerException
from .containerAuthorization import ContainerAuthorization, ContainerKeyPair
from .crypto import CipherWrapper
from pgpy import PGPKey, PGPMessage, PGPSignature

class Container:

    def __init__(self, initInfo=None, privKey=None, authData=None, meta=None, rootSig=None, data=[]):
        self.cipher = None
        if initInfo:
            self.__initFromInfo(initInfo, privKey)
        elif authData is not None and meta is not None and rootSig is not None:
            self.meta = meta
            if not type(authData) is ContainerAuthorization:
                raise ContainerException("authData invalid type")
            self.authorization_data = authData
            if not type(rootSig) is PGPSignature:
                raise ContainerException("rootSig invalid type")
            self.rootSignature = rootSig
            self.data = data
            self.verify()
            self.checkReleased()
        else:
            raise ContainerException("Not enough information to create container")

    def __initFromInfo(self, info, privKey):
        if not type(privKey) is PGPKey:
            raise ContainerException("Private key has to be provided to create container")
        if info.sharedKey is None:
            raise ContainerException("Can't create new container without AES Key")
        self.meta = info.meta
        self.authorization_data = ContainerAuthorization(ContainerKeyPair(info.authorPubKey,sharedKey=info.sharedKey))
        self.rootSignature = self.__calculateRootSignature(privKey)
        self.data = []
        # When the container has just been created we can unlock it by default
        # since it can only be created with the correct privKey anyway
        self.Unlock(privKey)
        pass

    def verify(self):
        #Make sure the base container is valid
        if not self.verifyRootSignature():
            raise ContainerException("Root signature invalid")
        #Keep track of which author keys have existed at what point
        authIdx = 1
        for i in range(len(self.data)):
            #Check that hash data is correct
            if not self.verifyEntry(i):
                raise ContainerException("HashData of entry {} invalid".format(i))
            # Check that every creatorId is less than the number of already verified AUTHORIZE entries
            # Without this check an AUTHORIZE entry could be added by anyone with the AES key
            # to get write permissions on the container, by signing the AUTHORIZE entry with the key it adds
            if self.data[i].creatorId >= authIdx:
                raise ContainerException("Key used to create entry not yet valid")
            # Check that an AUTHORIZE entry matched the expected next public key in authorize_data
            # If AUTHORIZE entry is valid advance authIdx to also accept the added pubkey AFTER this entry
            if self.data[i].type == ContainerEntryType.AUTHORIZE:
                if self.authorization_data.getKeyById(authIdx).pub.fingerprint == PGPKey.from_blob(self.data[i].data)[0].fingerprint:
                    authIdx+=1
                else:
                    raise ContainerException("Unexpected key being authorized in data entry {}".format(i))
                    
        #Verify that all entries in authorize_data have been verified by matching AUTHORIZE entries
        if authIdx-1 != len(self.authorization_data.extraKeys):
            raise ContainerException("Missing authorization entry for extra key {}".format(authIdx-1))

    def checkReleased(self):
        for i in range(len(self.data)):
            if self.data[i].type == ContainerEntryType.RELEASE:
                self.UnlockPublished(self.data[i].data)

    def rootInfoBlob(self):
        blob = b""
        blob += bytes(self.authorization_data.authorKey.pub)
        blob += b":"
        blob += bytes(self.authorization_data.authorKey.encShared)
        blob += b";"
        blob += self.meta['version'].encode()
        blob += b":"
        blob += self.meta['nonce']
        blob += b":"
        blob += self.meta['hashAlgo'].encode()
        blob += b":"
        blob += self.meta['cipher'].encode()
        blob += b";"
        return blob

    def rootInfoHash(self):
        m = hashlib.sha256()
        m.update(self.rootInfoBlob())
        return m.digest()

    def __calculateRootSignature(self, privKey):
        return privKey.sign(PGPMessage.new(self.rootInfoHash()))

    def verifyRootSignature(self):
        return self.authorization_data.authorKey.pub.verify(self.rootInfoHash(), self.rootSignature)

    def IsUnlocked(self):
        return self.cipher is not None

    def __unlockData(self):
        if not self.IsUnlocked():
            raise ContainerException("Can not unlock data in locked container")
        for entry in self.data:
            entry.Unlock(self.cipher)

    def __createCipher(self):
        self.cipher = CipherWrapper(self.meta['cipher'], self.sharedKey)
    
    def UnlockPublished(self, sharedKey):
        self.sharedKey = sharedKey
        self.__createCipher()
        self.__unlockData()

    def Unlock(self, privKey):
        if not type(privKey) is PGPKey:
            raise ContainerException("Not a private key: {}".format(privKey))
        self.sharedKey = self.authorization_data.getSharedKey(privKey)
        self.__createCipher()
        self.__unlockData()

    def GetCipher(self):
        if self.cipher is None:
            raise ContainerException("Container not unlocked")
        return self.cipher

    def release(self, privKey):
        if not self.IsUnlocked():
            self.Unlock(privKey)
        creatorId = self.authorization_data.getIdOfKey(privKey)
        releaseEntry = ContainerEntry(entryType=ContainerEntryType.RELEASE,
                                   creatorId=creatorId,
                                   title="Release Shared Key",
                                   data=bytes(self.sharedKey),
                                   encrypted=False)
        self.appendEntry(releaseEntry, privKey)

    def authorize(self, pubKey, privKey):
        if not self.IsUnlocked():
            self.Unlock(privKey)
        creatorId = self.authorization_data.getIdOfKey(privKey)
        self.authorization_data.authorize(pubKey, self.sharedKey)

        authEntry = ContainerEntry(entryType=ContainerEntryType.AUTHORIZE,
                                   creatorId=creatorId,
                                   title="Authorize {}".format(pubKey.fingerprint),
                                   data=bytes(pubKey),
                                   encrypted=False)
        self.appendEntry(authEntry, privKey)

    def appendEntry(self, entry, privKey):
        if not type(entry) is ContainerEntry:
            raise ContainerException("Can only append ContainerEntry")
        if len(self.data) == 0:
            rootHash = self.rootInfoHash()
            prevHashData = ContainerEntryHashData(clearHash=rootHash, storedHash=rootHash)
        else:
            prevHashData = self.data[-1].hashData
        #Calculate and sign hashes and check that signatures from priv key are valid
        entry.createHashData(prevHashData)
        entry.signHashData(privKey)
        if not entry.hashData.verify(self.authorization_data.getKeyById(entry.creatorId).pub):
            raise Exception("Privkey doesn't match creatorId public key")
        #Finally append entry to data array
        self.data.append(entry)

    def verifyEntry(self, idx):
        if idx<0 or idx>=len(self.data):
            raise ContainerException("Invalid entry index")
        entry = self.data[idx]
        if idx == 0:
            rootHash = self.rootInfoHash()
            prevHashData = ContainerEntryHashData(clearHash=rootHash, storedHash=rootHash)
        else:
            if entry.timestamp < self.data[idx-1].timestamp:
                raise ContainerException("Timestamp is older than previous entry")
            prevHashData = self.data[idx-1].hashData
        #Check that hashes are correct
        if not entry.hashData.matches(prevHashData, entry):
            return False
        #Check that hash signatures are correct
        return entry.hashData.verify(self.authorization_data.getKeyById(entry.creatorId).pub)