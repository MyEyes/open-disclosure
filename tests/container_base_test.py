from filelock import sys
from pgp_key_fixtures import *
from pgpy.errors import PGPError

import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from opendisclosure import Container, ContainerCreationInfo, ContainerEntry, ContainerEntryType, ContainerException

def test_createContainerInfo(researcher_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    assert ci is not None
    assert ci.authorPubKey.fingerprint == researcher_key.fingerprint
    assert ci.challenge is None #No challenge allowed for now
    assert ci.meta['version'] == "0.3"
    assert len(ci.meta['nonce']) > 8 #Totally arbitrary for now. TODO: Update based on actual data

def test_createContainer(researcher_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    c = Container(ci, researcher_key)
    assert c.authorization_data.authorKey is not None
    assert c.authorization_data.authorKey.pub.fingerprint == researcher_key.fingerprint
    assert c.sharedKey is not None
    c.verify() #Will raise exception on failure

def test_ContainerAppendText(researcher_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    c = Container(ci, researcher_key)
    testTitle = "Test Entry"
    testText = "This is some test data for this entry"
    testEntry = ContainerEntry(ContainerEntryType.TEXT, creatorId=0, title=testTitle, data=testText, encrypted=False)
    c.appendEntry(testEntry, researcher_key)
    assert len(c.data) == 1
    assert c.data[0].type == ContainerEntryType.TEXT
    assert c.data[0].encrypted == False
    assert c.data[0].title == testTitle
    assert c.data[0].data == testText

def test_ContainerAppendTextEncrypted(researcher_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    c = Container(ci, researcher_key)
    testTitle = "Test Entry"
    testText = "This is some test data for this entry"
    testEntry = ContainerEntry(ContainerEntryType.TEXT, creatorId=0, title=testTitle, data=testText, encrypted=True, cipher=c.GetCipher())
    c.appendEntry(testEntry, researcher_key)
    assert len(c.data) == 1
    assert c.data[0].type == ContainerEntryType.TEXT
    assert c.data[0].encrypted == True
    assert c.data[0].title == testTitle
    assert c.data[0].data == testText

def test_ContainerAppendInvalidCreatorId(researcher_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    c = Container(ci, researcher_key)
    testTitle = "Test Entry"
    testText = "This is some test data for this entry"
    testEntry = ContainerEntry(ContainerEntryType.TEXT, creatorId=1, title=testTitle, data=testText, encrypted=True, cipher=c.GetCipher())
    #Append should fail because creatorId is invalid
    with pytest.raises(ContainerException):
        c.appendEntry(testEntry, researcher_key)

def test_ContainerAppendInvalidPrivKey(researcher_key, thirdParty_key):
    ci = ContainerCreationInfo(researcher_key.pubkey)
    c = Container(ci, researcher_key)
    testTitle = "Test Entry"
    testText = "This is some test data for this entry"
    testEntry = ContainerEntry(ContainerEntryType.TEXT, creatorId=0, title=testTitle, data=testText, encrypted=True, cipher=c.GetCipher())
    #Append should fail because private key doesn't match creator public key
    with pytest.raises(PGPError):
        c.appendEntry(testEntry, thirdParty_key)
