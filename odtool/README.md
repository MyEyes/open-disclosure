# odtool.py
This utility is a CLI tool to create, modify or verify containers
And to print or extract the information contained in the container.

The tool supports several subcommands that are hopefully more or less self explanatory.

The tool does not currently support the use of the keyring and requires the private key to be supplied as a file on the file system

**The tool also does not protect against potential path traversal issues when extrating files from a container, if this is a concern you can specify "--convention idx" which will force exported entries to be named by their index rather than their title.**

## Usage
    usage: odtool.py [-h] [-f] [--allowKeyring] [--priv privKey] {create,verify,print,export,modify} ...

    Interact with Open Disclosure files

    positional arguments:
    {create,verify,print,export,modify}
                            Command
        create              Create a new container
        verify              Verify the integrity of a container
        print               Print container information
        export              Export information from container
        modify              Modify an existing container

    optional arguments:
    -h, --help            show this help message and exit
    -f, --force           Don't prompt and assume yes
    --allowKeyring        Allow the use of the users keyring
    --priv privKey        Private key to use