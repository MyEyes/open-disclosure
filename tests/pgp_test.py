import pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm

# These tests mainly exist to avoid having potentially confusing error messages
# in base the pgpy API changes or becomes buggy in other ways

def genKeyHelper():
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    uid = pgpy.PGPUID.new('Test User', comment='test', email='test@test.test')

    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
    return key

def test_PGP_keygen():
    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    assert key is not None
    uid = pgpy.PGPUID.new('Test User', comment='test', email='test@test.test')
    assert uid is not None

    key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
                hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
                ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
                compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])
    assert len(key.userids) == 1

def test_PGP_keyio(tmp_path):
    key = genKeyHelper()
    path = tmp_path / "testkey"
    with open(path, "w") as f:
        f.write(str(key))

    testkey, _ = pgpy.PGPKey.from_file(path)
    assert testkey.fingerprint == key.fingerprint
    assert bytes(testkey) == bytes(key)
    assert str(testkey) == str(key)
        
    
