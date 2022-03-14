import pytest
from testhelper import genPGPKey

@pytest.fixture
def researcher_key():
    return genPGPKey("Researcher", "researcher", "security@research.local")

@pytest.fixture
def vendor_key():
    return genPGPKey("Vendor", "vendor", "vulnerable@vendor.local")

@pytest.fixture
def thirdParty_key():
    return genPGPKey("Third Party", "Third Party", "third@party.local")