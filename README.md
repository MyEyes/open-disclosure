# Open Disclosure
The goal of **Open Disclosure** is to offer a more transparent way to perform security disclosures.

To achieve this the disclosure can be performed entirely in public in a cryptographically secure container file that is self contained.

This provides some additional security guarantees that the 

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