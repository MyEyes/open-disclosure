# Open Questions
This document is meant to serve as a basis for discussion of parts of the theory that are not yet part of the concept. For that reason it is more of a stream of consciousness of pros and cons of the questions being discussed.

The document will necessarily reference concepts from the *concept.md* document

## Timegating
It is possible to explicitly add a timegate to a container.

In an abstract sense this timegate is meant to guarantee the release of the containers shared key at some point in the future.

This release does not necessarily have to happen at a specific time, although that's a desirable property.
It should however guarantee (to some degree of certainty) when the shared key will be released AT THE EARLIEST, to prevent violating a disclosure deadline.

The main purpose is to guarantee that the shared key will eventually become public regardless of the actions of any of the containers authorized parties.

This should most definitely be an optional feature of a container and not a requirement.

## Kinds of timegates

### Independent parties
The shared key or parts of the shared key can be handed off to independent parties with instructions to release the information at a specific time.

This feels very unelegant and also potentially gives these independent parties premature access to the containers contents

### Compute challenges
A compute challenge can be generated that will produce the shared key as its solution. I really like this concept in theory because it removes the need to trust anybody to guarantee the (eventual) release of the containers information, but it has some problems.

It's very difficult to guarantee a minimum time to compute the solution assuming that almost arbitrary amounts of computation can be used to solve the challenge, while also guaranteeing that the challenge can conceivably be solved.

Such a challenge would have to be difficult or impossible to parallelize and maybe be bound by memory latency rather than compute time.

There is likely some academic work here that I am unaware of.

## Handling revocation of public keys
This is an issue that limits the aspect of the guarantee of self containedness.
I'm not sure about all of the implications of this

## Attestation files
It might be a good idea to define a standard method to generate and verify attestation files from the information inside a container, even when still encrypted.

This might make verifying and proving especially truncation of containers easier and more storage efficient.

## Signature/Verification algorithm
At the moment the library and specification simply use PGP signatures for signing and verification of information.
These signatures are very large though and contain additional information that is not strictly needed.
It might be feasible to include the method for signature and verification as part of a containers meta data to offer more compact methods such as Schnorr signatures.
I'm not sure at this point if it's possible to use the PGP keys to easily sign and verify using arbitrary other signature algorithms.

## Salting of Data Entry Hash Data Signatures
*See **potential_attacks.md** Hash collision of DataEntry.HashData.StoredHash*

To reduce the risk of reusing signatures to forge entries, if a hash collision is found it might be sensible to instead sign not just the hash, but the hash with appended container nonce (and a data entry nonce).