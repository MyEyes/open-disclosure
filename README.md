# Open Disclosure
The goal of **Open Disclosure** is to offer a more transparent way to perform security disclosures.

To achieve this the disclosure can be performed entirely in public in a cryptographically secure container file that is self contained.

This provides some additional security guarantees that the current standard process for disclosing vulnerabilities does not.

## Disclaimer
**This repository is currently very work in progress.**

Tests, the specification and the reference implementation are likely to be incomplete and contain bugs or other issues. I am putting all of this public as a first draft to gather feedback and to allow others to point out issues both theoretical and in the implementation.

**Please open issues on this repository if anything is unclear, should be considered or explicitly elaborated on, any problems with the theory and or implementation issues. I am hoping to gather as much input as possible.**

If you'd rather not use github, feel free to contact me on twitter (@firzen14) instead.

## Repository Content
This repository contains a first draft of the specification, a reference implementation of the concept, and a CLI tool to allow easy experimentation with the involved concepts.

### opendisclosure
A PoC implementation as a python library.
Currently only supports AES256-GCM with sha256 hashes, but can easily be expanded to handle arbitrary ciphers and hashes.

### odtool
A CLI tool using the **opendisclosure** library.
This tool serves both as example code for how to use the library, as well as as an easier way to experiment with the concepts.

### test
A collection of pytest testcases for the **opendisclosure** library.

### theory
Contains a description of the basic idea, more in depth theory behind the concept, a draft of the specification and an examination of the security properties that can be guaranteed.