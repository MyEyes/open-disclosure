# Implementation
This document is supposed to be an abstract description of the/an implementation of a container as described in **concept.md**.  
It will especially focus on how this implementation produces the guarantees required by a container.

Information that is especially relevant to those guarantees will be marked by "!!!" in the document, to make it easier to find the relevant sections.

*Authors Note: "**the** container" will mean a container of this specific implementation, whereas "**a** container" will mean an abstract container as described in **concept.md***

# Container Structure
A container contains four main components
* **Meta** information describing the parameters used in the container
* An **authorization structure** containing public keys and encrypted shared keys
* A **root signature** signing a hash of the meta information and the original authorization structure
* The **data entries** stored in the container

## Meta Information
The meta information stored in the container contains the following 4 data points:
* Version
* HashAlgo
* Cipher
* Nonce

This information should be a full description of how cryptography and validation of information in the container should be performed.

The **Version** is required in case the process changes, so that an old container can still be validated.

The **HashAlgo** describes which hashing algorithm should be used to calculate the digests of information stored in the container to verify its integrity.

The **Cipher** describes which cipher should be used to encrypt the information stored in the container.

The **Nonce** is required to prevent potential hash reuse.

*Authors Note: When the rest of the document mentions hashing or a cipher/encryption it referes to the specific hash algorithm and encryption method chosen in the meta information.*

## Authorization Data
The authorization data contains information about who has been granted write access to the container, as well as enabling read access to the container before the shared key is publicly released.

The authorization data field consists of tuples of public key and the encrypted shared key.

The tuple contains
* A PGP public key
* The shared key **encrypted** with the tuples public PGP key.

*Authors Note: I currently call them ContainerKeyPair in code, I should probably rename them to ContainerAuthorizationTuple*

Authorization data consists of two sets of such tuples.

* A single author key tuple
* An array of extra key tuples

Every container **must** contain an author key tuple  
A new empty container **must not** contain any extra key tuples.

## Root Signature
The root signature is used to verify the integrity of the meta information as well as the original author key tuple.

This signature signs a hash digest of the meta information and the author authorization tuple.
This hash digest is not explicitly stored, since it can always be recalculated and verified.

*Authors Note: In the code and in the rest of this document I will call this digest the rootInfoHash*

The signature of the rootInfoHash can be verified using the author public key from the authorization structure.

It is important that the rootInfoHash can be verified since it forms the anchor to verify the integrity of the rest of the document.

## Guarantees of an empty container
A container that only contains the already described information **meta**, **authorization data** of just the original author and a valid **root signature** is the minimum valid container.  
(It should probably also contain an empty data array, but that's an implementation detail)

It's important to establish which properties are guaranteed at this point, so that the rest of the document can build on this.

**An empty container is self contained.**  
Anybody can verify that the container has been created by the owner of the public key stored in the *authorization data* without requiring any external information.  
This can be done by verifying the root signature by calculating the rootInfoHash and checking the signature with the public key.

**The empty container is based on PGP**  
The implementation uses a PGP public key for the authorization data.

**The empty container is independently verifiable**  
See self contained above. So far the only encrypted information stored in the container is the encrypted shared key in the authorization data.

**The empty container delivers all guarantees related to data storage**  
Almost all other guarantees are provided by default since no additional information is stored.

## Data
Data added to the container is appended to an array of data entries.
These data entries contain the following:
* a numerical **creator id**
* a unix **time stamp**
* an entry **type**
* an **encrypted** boolean
* a blob of **stored data**
* a cleartext **title**
* a **hash data** entry

### Data Entry Creator Id
The creator id of a data entry is an index into the authorization data of the container to describe which authorized party appended the data entry.

### Data Entry Time Stamp
The timestamp is mainly added for convenience of following the timeline of the disclosure. It is not currently verified and the **hash data** contains a time stamp in the signatures as well, which makes this entry relatively superfluous

### Data Entry Type
A data entry can have one of 4 types:
* TEXT
* FILE
* AUTHORIZE
* RELEASE

 **TEXT** and **FILE** are used to store arbitrary information in the container,  
 whereas **AUTHORIZE** and **RELEASE** are meta entries that modify access to the container.

The details of how these different types are interpreted are described further down.

### Data Entry Encrypted
The encrypted boolean describes wether the data entry is encrypted or not.

**AUTHORIZE** and **RELEASE** entries **must not** be encrypted. Since these entry types modify access to the container they have to be verifiable by anyone.

### Data Entry Title
An optional title of the data entry.  
The title is unencrypted as of now.
*Authors Note: Mainly due to me being lazy about writing additional code to handle encryption and decryption of the title. I don't think it should be a security issue either way. It could maybe save careless people from accidentally leaking information in the title though*

For **TEXT** type entries this can be anything.  
For **FILE** type entries this can be anything as well, but it make sense to default this to a sensible file name.

For **AUTHORIZE** and **RELEASE** type entries the library will automatically generate them, since the title is entirely irrelevant. (All information of these entries is public anyway)

### Data Entry Stored Data
The stored data entry simply contains a blob of the encrypted or unencrypted data stored in the entry.

### Data Entry Hash Data
The hash data contains 2 tuples of hashes and signatures.
* Clear hash
* Clear signature
* Stored hash
* Stored signature

**Hash calculation**  
*Clear hash*  
The hash is calculated as a digest of the creatorId, the title if it exists, the decrypted information and the previous entrys clear hash.

*Stored hash*  
The hash is calculated as a digest of the creatorId, the title if it exists, the bytes of the information as stored in the entry and the previous entrys stored hash.

!!! Since the clear hash depends on the decrypted information it is not possible to alter an entries encrypted flag without causing the clear hash to not match anymore.

!!! Since the hashes depend on the creatorId and the entries title and information an entry can not be modified without causing the hashes to not match anymore.

!!! Since the hashes depend on the previous entries hashes, no entry can be omitted without causing any subsequent entries to not match the hash data anymore.

!!! The stored hash can be verified by anyone at any point, by recalculating it

!!! The clear hash can be verified by anyone with access to the shared key, by recalculating it

!!! The hashes do **not** depend on the entry type and timestamp. Timestamp is a convenience feature as mentioned above and changing an entrys type should not cause any security issues. (See **potential_attacks.md** Altering Data Entry Type)

*First entry*  
Since the very first data entry won't have a previous entrys hash, it uses the rootInfoHash instead.

*Authors note: It's probably worth making sure the clear and stored hashes are different, so the maybe the rootInfoHash should have a salt like CLEAR or STORED appended for the first entry hash calculation*

**Signature calculation**  
The calculated hashes are signed with the private key corresponding to the public key referenced by the creatorId of the entry.

!!! This signature can be verified by anybody since the public key is part of the containers authorization data.

!!! Even if the data entry is later deleted or the container truncated, anyone that has saved a copy can prove it existed and was made by someone with access to the private key by producing a valid hash/signature pair

## Details of Data Entry Types

### Data Entry Type TEXT
This data entry contains data that should be interpreted as clear text.  
The current tooling will export such an entry as a .txt file by default and will display the text when printing such an entry.

### Data Entry Type FILE
This data entry contains data that should be interpreted as a (binary) file.  
The current tooling will export such an entry as a file named after the entries title by default and won't display the (potentially binary) data when printing such an entry.

### Data Entry Type AUTHORIZE
*Must be unencrypted*  
This data entry contains an unencrypted PGP public key that should be allowed write access to the container.  
For every AUTHORIZE entry there **MUST** be a corresponding tuple in the authorization data extra keys containing the public key and encrypted shared key.

All of the extra keys **MUST** be in the same order as the corresponding AUTHORIZE entries.

### Data Entry Type RELEASE
*Must be unencrypted*  
This data entry contains the unencrypted shared key of the container.
Such an entry effectively releases all of the encrypted information in the container publicly.

*Authors Note: This is purely for convenience it would be possible to simply check every unencrypted TEXT or FILE entry to see if its the shared key. This type just makes it easier to automatically decrypt a container once its released*

## Verification of a container

*If the shared key is not known only the stored hash of each encrypted entry can be verified*

To verify a container, the following steps should be taken:

1. [Verify the rootInfoHash and root signature](#root-signature)
2. Set the last valid key index to 1
3. For each entry  
    1. [Check that the hash data matches](#data-entry-hash-data)
    2. [Check that the signatures are valid](#data-entry-hash-data)
    3. [Check that the creatorId of the entry is less than the last valid extra key](#data-entry-type-authorize)
    4. If the entry is of type AUTHORIZE
        * [Check that the entries public key matches the expected next key in the extra keys](#data-entry-type-authorize)
        * Increment last valid key index
4. Check that last valid key index is one greater than the number of keys to verify that all keys in the authorization data section have corresponding AUTHORIZE entries

## Accessing a containers encrypted data

To access the encrypted information in a container, the container either needs to contain a RELEASE entry making all content public, or one needs to be in possesion of the corresponding private key of one of the tuples in authorization data.

If an authorized private key is known, the encrypted shared key of the authorization tuple can be decrypted to retrieve the containers shared key.

If the shared key is released, it can be retrieved from the RELEASE entry.

For every encrypted entry the cipher specified in the containers meta information can then be used to decrypt the entries stored data.


## Evaluation of desired container properties

### Public
This property is mainly a matter of procedure and can't really be offered by the implementation.

### Self contained
This property is guaranteed.  
No external information is needed to verify the integrity of the container.
See [Verification of a container](#verification-of-a-container)

There might be an issue related to revocation of keys however. See **open_questions.md - Handling revocation of public keys**

### Cryptographically secure
This property is guaranteed as far as the container goes.  

It is guaranteed in so far as the chosen cipher and the authorized parties security of private keys provide.
It is therefore as secure or insecure as other modes of communication between the same parties with the same cipher.

### Read-Only unless authorized publicly
This property is guaranteed.  
Since any entrys signatures need to be verified by public keys from the containers authorization data, no data can be appended and pass the verification check without a public record of the authorization and without possesion of the corresponding private key.
See [Data Entry Hash Data](#data-entry-hash-data)

### Based on PGP
This property is guaranteed.  
See [Guarantees of an empty container](#guarantees-of-an-empty-container) in particular
and the rest of the document in general.

### Independently Verifiable
This property is guaranteed.  
The only relevant case to consider is that of an outside party without access to the shared key.
Such a party can verify:
* The root hash
* The root signature
* Every entries stored hash
* Every entries stored and clear signature

So the existence of the disclosure, the author of each data entry, the integrity of the stored information, the order of entries and the completeness of the information, can be independently verified without getting access to the containers encrypted information.

The integrity of the decrypted information can additionally be verified by anyone with access to the shared key, which can also be done retroactively once the container is released.

See [Root Signature](#root-signature)  
See [Data Entry Hash Data](#data-entry-hash-data)

### Provable
This property is guaranteed.
Since a containers data can not be altered or omitted without altering the hashes and failing verification, the only case to consider is truncation.

The containers are self contained, allow the independent verification of the authorship of each entry and can be copied by anyone as long as the container is public.  

A copy of such a container is sufficient to prove that an entry in such a container existed at some point in the past and that it was created by somebody with access to the specific private key that signed that entry.

This means that while a truncated container is still valid as per [#Verification of a container](#verification-of-a-container), it is possible for anybody to prove that such a truncation has been performed and for anybody else to independelty verify that that proof is correct.

### Append only
This property is guaranteed.  
Should any entry of a container be modified or omitted that isn't the last entry of the container it will make all subsequent hashes invalid. (See [Data Entry Hash Data](#data-entry-hash-data))

For that reason the only case to consider is the author of the last entry retroactively altering it or truncating the container, which can be proven to have happened as described in [Provable](#provable)

### Release-able
This property is guaranteed.  
See [Data Entry Type RELEASE](#data-entry-type-release)