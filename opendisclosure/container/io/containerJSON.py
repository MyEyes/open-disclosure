import json
import base64

from itsdangerous import base64_decode

from opendisclosure.container.containerEntry import ContainerEntry, ContainerEntryHashData
from ... import Container, ContainerAuthorization, ContainerKeyPair, ContainerEntryType, ContainerEntry
import pgpy

class ContainerJSON:
    @classmethod
    def ContainerToJSONFile(cls, container, path):
        with open(path, "w") as f:
            f.write(cls.ContainerToJSON(container))

    @classmethod
    def ContainerToJSON(cls,container):
        contDict = {}
        contDict['meta'] = container.meta.copy()
        contDict['meta']['nonce'] = base64.b64encode(contDict['meta']['nonce']).decode()
        contDict['rootSig'] = base64.b64encode(bytes(container.rootSignature)).decode()
        contDict['authorization'] = cls.__encodeAuthorization(container.authorization_data)
        contDict['data'] = cls.__encodeData(container.data)
        return json.dumps(contDict)

    @classmethod
    def __encodeAuthorization(cls, authorization):
        authDict = {}
        authDict['authorKey'] = cls.__encodeAuthorizationKeyPair(authorization.authorKey)
        authDict['extraKeys'] = []
        # Doing it this way because the order of keys really matters
        # And I'm not sure if iterating over an array with an iterator guarantees the order
        for i in range(len(authorization.extraKeys)):
            authDict['extraKeys'].append(cls.__encodeAuthorizationKeyPair(authorization.extraKeys[i]))
        return authDict

    @classmethod
    def __decodeAuthorization(cls, authDict):
        authorKey = cls.__decodeAuthorizationKeyPair(authDict['authorKey'])
        extraKeys = []
        # Doing it this way because the order of keys really matters
        # And I'm not sure if iterating over an array with an iterator guarantees the order
        for i in range(len(authDict['extraKeys'])):
            extraKeys.append(cls.__decodeAuthorizationKeyPair(authDict['extraKeys'][i]))
        return ContainerAuthorization(authorKey, extraKeys)

    @classmethod
    def __encodeAuthorizationKeyPair(cls, authorizationKeyPair):
        pairDict = {}
        pairDict['pub'] = base64.b64encode(bytes(authorizationKeyPair.pub)).decode()
        pairDict['encShared'] = base64.b64encode(authorizationKeyPair.encShared).decode()
        return pairDict

    @classmethod
    def __decodeAuthorizationKeyPair(cls, pairDict):
        return ContainerKeyPair(pgpy.PGPKey.from_blob(base64.b64decode(pairDict['pub']))[0],
        encSharedKey=base64.b64decode(pairDict['encShared']))

    @classmethod
    def __encodeData(cls,data):
        dataArr = []
        for i in range(len(data)):
            dataArr.append(cls.__encodeEntry(data[i]))
        return dataArr

    @classmethod
    def __decodeData(cls, dataArr):
        data = []
        for i in range(len(dataArr)):
            data.append(cls.__decodeEntry(dataArr[i]))
        return data

    @classmethod
    def __encodeEntry(cls, entry):
        entryDict = {}
        entryDict['encrypted'] = entry.encrypted
        entryDict['title'] = entry.title
        entryDict['timestamp'] = entry.timestamp
        entryDict['type'] = entry.type.name
        entryDict['creatorId'] = str(entry.creatorId)
        entryDict['storedData'] = base64.b64encode(entry.storedData).decode()
        entryDict['hashData'] = cls.__encodeEntryHashData(entry.hashData)
        return entryDict

    @classmethod
    def __decodeEntry(cls, entryDict):
        return ContainerEntry(entryType=ContainerEntryType[entryDict['type']],
                              creatorId=int(entryDict['creatorId']),
                              title=entryDict['title'],
                              storedData=base64.b64decode(entryDict['storedData']),
                              encrypted=bool(entryDict['encrypted']),
                              hashData=cls.__decodeEntryHashData(entryDict['hashData']),
                              timestamp=int(entryDict['timestamp']))

    @classmethod
    def __encodeEntryHashData(cls, hashData):
        hashDict = {}
        hashDict['clearHash'] = base64.b64encode(hashData.clearHash).decode()
        hashDict['storedHash'] = base64.b64encode(hashData.storedHash).decode()
        hashDict['clearSig'] = base64.b64encode(bytes(hashData.clearSig)).decode()
        hashDict['storedSig'] = base64.b64encode(bytes(hashData.storedSig)).decode()
        return hashDict
    
    @classmethod
    def __decodeEntryHashData(cls, hashDict):
        return ContainerEntryHashData(clearHash=base64.b64decode(hashDict['clearHash']),
                                      storedHash=base64.b64decode(hashDict['storedHash']),
                                      clearSig=pgpy.PGPSignature.from_blob(base64.b64decode(hashDict['clearSig'])),
                                      storedSig=pgpy.PGPSignature.from_blob(base64.b64decode(hashDict['storedSig'])))

    @classmethod
    def JsonToContainer(cls, jsonStr):
        contDict = json.loads(jsonStr)
        meta = contDict['meta']
        meta['nonce'] = base64.b64decode(meta['nonce'])
        rootSig = pgpy.PGPSignature.from_blob(base64.b64decode(contDict['rootSig']))
        authorization = cls.__decodeAuthorization(contDict['authorization'])
        data = cls.__decodeData(contDict['data'])
        return Container(authData=authorization, rootSig=rootSig, meta=meta, data=data)

    @classmethod
    def JsonFileToContainer(cls, path):
        with open(path, "r") as f:
            return cls.JsonToContainer(f.read())