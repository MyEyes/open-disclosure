# Potential Attacks
This document should describe potential attacks against the containers and how they are (hopefully) mitigated.

## Hash collision of DataEntry.HashData.StoredHash
Since only the hash digest of a data entry is signed, if a hash collision for the stored data of an entry is found it could be possible to reuse the signature to forge a data entry with a valid stored hash signature without needing access to the containers shared key. Since the same public key will potentially sign quite a few such hashes the chance of finding a hash collision might increase over time.

From the perspective of anyone with access to the shared key, this risk is fully mitigated by the existence of a ClearHash of the decrypted information of a data entry, since it would be impossible for an attacker to predict the clear hash to cause a collision there as well.

From the perspective of anyone without access to the shared key, this risk is currently at least partially mitigated by the fact that the signatures contain timestamps which would not match the time a new entry is appended.  
It is worth considering this possibility regardless in case other signature methods are used in the future.

Additionally once the containers shared key becomes public, it is possible to retroactively falsify such an entry.

## Altering Data Entry Type
Since the type field is not part of an entrys hash digests it is possible to alter the type field without invalidating the entries hash data. This does however not have any security implications as far as I can tell.

The distinction of **TEXT** and **FILE** is purely for convenience and has no security implications, so converting between the two is not a problem.

Changing **TEXT** or **FILE** to **AUTHORIZE** is only possible if the entry is unencrypted and contains only a valid PGP public key, but will still fail since there won't be a corresponding encrypted shared key in the authorized data section.

Changing **TEXT** or **FILE** to **RELEASE** is only possible if the entry is unencrypted and contains the correct shared key, in which case it should probably have been **RELEASE** type to begin with.

Changing **AUTHORIZE** to something else will make the container invalid and is thus not any different from deliberately corrupting it.

Changing **RELEASE** to something else will still contain the clear text shared key and is for that reason at most inconvenient.