# Concept

The main idea of Open Disclosure centers around a container.

The container is used as a data store to facilitate the transfer of information between all involved parties.  
It is intended to provide aditional security guarantees and transparency.

With these properties guaranteed the whole disclosure process can be performed in a **publicly accessible** container, to allow more transparency and to allow independent parties to follow the disclosure process and to verify that the information is complete and unaltered, as well as verifying the decrypted information once the disclosure process is complete.

# Container properties

## Public
The container should be public to allow anybody access to the meta information contained and to allow independent verification.

## Self contained
The container has to be self contained.
Any valid container needs to be verifiable without needing to consult any outside sources.

This should also ease the integration into existing processes, since a single file can be used to store and transfer all information related to the disclosure.

## Cryptographically secure
The encrypted data stored in the container should be inaccessible to any party that has not been explicitly given access. Even if the container is public.

## Read-Only unless authorized publicly
Only authorized parties should be able to add information or grant access to the container.

The list of authorized parties has to be contained in the container.

Write access should be enforced cryptographically, by requiring signatures of appended information that can be verified using the list of authorized parties.

## Based on PGP
To ease adoption the containers authorization structure should be based on PGP.

*Authors note: Unlike most other properties which are rather abstract, this one is deliberately concrete to allow a discussion about particular details of how to make adoption and integration of this kind of process as easy as possible.*

Parties are granted access to the container by appending their public key and the shared key encrypted with that public key to the authorization structure.

Signatures can be verified using these public keys.

## Independently Verifiable
The integrity and completeness of the data stored in the container needs to be verifiable by independent parties, even if they can not decrypt the information stored in the container.

## Provable
If anybody, even an independent party without the ability to decrypt the stored information, witnesses the modification of a container, they need to be able to prove that such a modification has taken place.

## Append only
A container should only ever allow information to be added, rather than altered or removed. If information is altered or removed it should be possible to independently verify and prove that this has taken place.

## Release-able
*Authors Note: Is "release-able" a word? Open for suggestions here.*

A container should allow all information to be eventually released, without requiring the alteration of any of the contained information of the container.

For that reason the container should contain a shared key that is used to encrypt and decrypt information stored in the container.

The release of this information can then be performed by publishing the shared key.

*Authors Note: This still does not allow write access to the container, since even with access to the shared key to decrypt information no valid signature can be generated for appended information.*

# Missing and partial guarantees and issues

## Trust of authorized party required for release
In the current version of this concept one of the authorized parties is required to release the shared AES key to the public to eventually release the information in the container.

This is of course also the case with the current disclosure process, but it might be possible to remove even that trust requirement. *(See open_questions.md)*

## Truncation
Since the containers are append only and self contained, any previous version of a container has to be valid and pass verification as well.
This means that a container can be truncated to a previous valid state.

If a later state of the container has been public and was saved by anybody they can however prove that such a truncation has taken place even without access to the encrypted information.

## Premature information release by malicious trusted party
The encrypted information stored in the container can be released by anybody with access to the decryption key.

For that reason it is not possible to guard against the public release of the decrypted information by a trusted party acting maliciously.

This problem is completely unavoidable as far as I know, but is explicitly stated for completeness.

# Goal

The goal of this approach is to make several things possible or easier, that would otherwise be impossible or difficult to do.

In particular it is meant to require as little trust as possible between all involved parties. And to allow for more transparency of security disclosure processes.

## Oversight
Since the process is meant to happen in public it allows independent oversight of the process.
Especially without giving access to protected information to any additional parties that would have to be trusted and independent.

This is particularly relevant for disclosures through a third party like bug bounty programs, the ZDI or government agencies.

Since alteration of the stored information is provable, an agency or company overseeing the process can reliably prove if foul play has taken place, even without being granted access to any of the encrypted information.
This could provide the ability to levy fines or other penalties on the parties subject to such oversight.

## Anonymity
Since the process is meant to happen in public, a researcher looking to disclose a vulnerability does not have to contact the affected vendors directly.
It is instead possible to publicly place such a container anywhere on the internet.

## Transparency
Since the containers are meant to be public the process and timeline are necessarily public knowledge.
Additionally the fact that a disclosure is taking place and any potential disclosure deadline can be public information as well.

## Guaranteed disclosure
When disclosing through additional parties, no trust is necessary to guarantee the vendor will get access to the information.

Since the container is public and allows anonymous interaction, if a researcher wishes to disclose through a third party, they can grant access to the container without having to rely on the third party.

Access to the container can be granted to the affected vendor immediately or after a delay agreed upon with the third party.

