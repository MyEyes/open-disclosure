#!/usr/bin/python3
import sys
import os
from os.path import exists
from argparse import ArgumentParser
import pgpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from opendisclosure import *
from opendisclosure.container.io.containerJSON import ContainerJSON

######## PRINT HELPERS
def printContainerMeta(container):
    creator = container.authorization_data.getKeyById(0).pub.userids[0]
    print("="*128)
    print("Container Meta Info")
    print("="*128)
    print("\tCreator\t   : {}".format(creator))
    for k in container.meta:
        print("\t{: <11}: {}".format(k.capitalize(),container.meta[k]))
    print("\tNumEntries : {}".format(len(container.data)))
    if len(container.authorization_data.extraKeys) > 0:
        print("="*128)
        print("Authorized Users")
        for key in container.authorization_data.extraKeys:
            print("\t{}".format(key.pub.userids[0]))

def printContainerData(container, entries=None):
    print("Printing {} data entries".format(len(container.data)))
    if not entries:
        entries = range(len(container.data))
    for idx in entries:
        if idx<0 or idx>=len(container.data):
            print()
            print("="*128)
            print("{}- DOES NOT EXIST".format(idx))
            print("="*128)
            continue
        entry = container.data[idx]
        timestamp = entry.timestamp
        author = container.authorization_data.getKeyById(entry.creatorId).pub.userids[0]
        print()
        print("="*128)
        print("{}-{}@{}: {}{} - {}".format(idx, author, timestamp, "*" if entry.encrypted else "",entry.type.name, entry.title))
        print("="*128)
        if(entry.type == ContainerEntryType.TEXT):
            if entry.encrypted and not entry.IsUnlocked():
                print("<Encrypted Text>")
            else:
                print(entry.data)
        elif(entry.type == ContainerEntryType.FILE):
            if entry.encrypted and not entry.IsUnlocked():
                print("<Encrypted File>")
            else:
                print("<File contents are not printed>")
        elif(entry.type == ContainerEntryType.RELEASE):
            print("Shared AES key published")
        elif(entry.type == ContainerEntryType.AUTHORIZE):
            key = pgpy.PGPKey.from_blob(entry.data)[0]
            print("Authorizing {} for container".format(key.userids[0]))

############### HELPER FUNCTIONS
def confirm(prompt, defVal=True):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(prompt+" (Y/n): " if defVal else " (y/N): ").lower()
        if len(answer)==0:
            return defVal
    return answer == "y"

def loadContainer(path):
    return ContainerJSON.JsonFileToContainer(path)

def writeContainer(args, c, path):
    if exists(path):
        if not args.force:
            if not confirm("File {} exists, overwrite?".format(path)):
                return
    ContainerJSON.ContainerToJSONFile(c,path)
        

def getPrivKey(args, container=None):
    if not args.priv:
        return None
    #TODO: add ability to load a key from keyring
    return pgpy.PGPKey.from_file(args.priv)[0]

########## COMMANDS

########## MODIFY COMMANDS
def addModifySubparser(subparsers):
    modify_parser = subparsers.add_parser("modify", help="Modify an existing container")
    modify_parser.add_argument('container', type=str, metavar="path", help="Container to append to")
    return modify_parser.add_subparsers(help="Command", required=True, dest="cmd")

######### APPEND COMMAND
def addCmdAppend(subparsers):
    append_parser = subparsers.add_parser("append", help="Append a new entry")
    append_parser.add_argument('--clear', action='store_true', help="Don't encrypt added entry")
    append_parser.add_argument('--out', type=str, metavar="outfile", help="Output file, if not specified default to container path")
    append_parser.add_argument('type', choices=['text', 'file'])
    append_parser.add_argument('title', type=str, metavar="title", help="Title for the new entry")
    append_parser.add_argument('data', type=str, metavar="data/@file", help="Data or filepath to data to append")
    return {'append': cmdAppendHandler}

def cmdAppendHandler(args):
    outfile = args.container
    if args.out:
        outfile = args.out
    data = args.data
    if args.data[0] == '@':
        mode = "r" if args.type == "text" else "rb"
        with open(args.data[1:], mode) as f:
            data = f.read()
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if not privkey:
        raise Exception("Private key required to modify container")
    c.Unlock(privkey)

    creatorId = c.authorization_data.getIdOfKey(privkey)
    entryType = ContainerEntryType.FILE if args.type == "file" else ContainerEntryType.TEXT
    if args.clear:
        entry = ContainerEntry(entryType, creatorId=creatorId, title=args.title, data=data, encrypted=False)
    else:
        entry = ContainerEntry(entryType, creatorId=creatorId, title=args.title, data=data, encrypted=True, cipher=c.GetCipher())
    
    c.appendEntry(entry, privkey)
    writeContainer(args,c,outfile)

######### AUTHORIZE COMMAND
def addCmdAuthorize(subparsers):
    auth_parser = subparsers.add_parser("authorize", help="Authorize access for a new public key")
    auth_parser.add_argument('pub', help="Public key to add to list of authorized keys")
    return {'authorize': cmdAuthorizeHandler}

def cmdAuthorizeHandler(args):
    outfile = args.container
    if args.out:
        outfile = args.out
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if not privkey:
        raise Exception("Private key required to modify container")
    else:
        c.Unlock(privkey)
    writeContainer(args,c,outfile)

######### RELEASE COMMAND
def addCmdRelease(subparsers):
    release_parser = subparsers.add_parser("release", help="Release all information in the container by publishing the shared AES key")
    return {'release': cmdReleaseHandler}

def cmdReleaseHandler(args):
    outfile = args.container
    if args.out:
        outfile = args.out
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if not privkey:
        raise Exception("Private key required to modify container")
    else:
        c.Unlock(privkey)
    c.release(privkey)
    writeContainer(args,c,outfile)

######### CREATE COMMAND
def addCmdCreate(subparsers):
    create_parser = subparsers.add_parser("create", help="Create a new container")
    create_parser.add_argument('path', help="Output path for new container")
    return {'create': cmdCreateHandler}

def cmdCreateHandler(args):
    privkey = getPrivKey(args)
    if not privkey:
        raise Exception("Couldn't load private key")
    pubkey = privkey.pubkey
    ci = ContainerCreationInfo(pubkey)
    c = Container(ci, privkey)
    writeContainer(args, c, args.path)

######### VERIFY COMMAND
def addCmdVerify(subparsers):
    # TODO: add additional modes of verification
    # like using the signed entry hashes to verify
    # that between disclosure and release of container
    # the container wasn't truncated
    verify_parser = subparsers.add_parser("verify", help="Verify the integrity of a container")
    verify_parser.add_argument('container', type=str, metavar="path", help="Container to verify")
    return {'verify': cmdVerifyHandler}

def cmdVerifyHandler(args):
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if not privkey:
        if not c.IsUnlocked():
            print("WARNING: No private key for encrypted container, can only partially verify")
    else:
        c.Unlock(privkey)
    c.verify()

######### PRINT COMMAND
def addCmdPrint(subparsers):
    print_parser = subparsers.add_parser("print", help="Print container information")
    print_parser.add_argument('--entries', type=int, nargs='*', help="Only display information for specified entries")
    print_parser.add_argument('container', type=str, metavar="path", help="Container to print information of")
    print_parser.add_argument('action', choices=["meta", "data"])
    return {'print': cmdPrintHandler}

def cmdPrintHandler(args):
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if privkey:
        c.Unlock(privkey)
    entries = None
    if args.entries:
        entries = args.entries
    if args.action == "meta":
        printContainerMeta(c)
    elif args.action == "data":
        printContainerData(c, entries)

######### EXPORT COMMAND
def addCmdExport(subparsers):
    export_parser = subparsers.add_parser("export", help="Export information from container")
    export_parser.add_argument('--entries', type=int, nargs='*', help="Which entries to export, default=all")
    export_parser.add_argument('--convention', type=str, choices=['idx', 'title'], default="title", help="Create file name from title or entry idx")
    export_parser.add_argument('--spaceRep', type=str, default="_", help="Convert spaces in title to this character for filename")
    export_parser.add_argument('--textSuffix', type=str, default=".txt", help="Suffix appended to exported text entries")
    export_parser.add_argument('--skipExisting', action='store_true', help="Skip entry if corresponding file already exists")
    export_parser.add_argument('container', type=str, metavar="path", help="Container to print information of")
    export_parser.add_argument('prefix', type=str, help="String that is prepended to determine export filename")
    return {'export': cmdExportHandler}

def cmdExportHandler(args):
    c = loadContainer(args.container)
    privkey = getPrivKey(args, c)
    if privkey:
        c.Unlock(privkey)
    entries = range(len(c.data))
    if args.entries:
        entries = args.entries
    for idx in entries:
        if idx<0 or idx>=len(c.data):
            print("Entry#{} does not exist, skipping".format(idx))
        entry = c.data[idx]
        if not entry.IsUnlocked():
            print("Entry#{} is encrypted, skipping".format(idx))
            continue
        if entry.type in [ContainerEntryType.AUTHORIZE, ContainerEntryType.RELEASE]:
            print("Entry#{} is meta type, skipping".format(idx))
            continue
        
        if args.convention == 'title':
            path = args.prefix+entry.title.replace(" ", args.spaceRep)
        elif args.convention == 'idx':
            path = args.prefix+str(idx)
        else:
            raise Exception("Unknown convention")

        if entry.type == ContainerEntryType.TEXT:
            path += args.textSuffix
            mode = "w"
        elif entry.type == ContainerEntryType.FILE:
            mode = "wb"

        if exists(path) and not args.force:
            if args.skipExisting:
                continue
            if not confirm("File {} already exists, overwrite?".format(path)):
                continue
        with open(path, mode) as f:
            f.write(entry.data)

    

######### MAIN
if __name__ == '__main__':
    parser = ArgumentParser(description="Interact with Open Disclosure files")
    parser.add_argument('-f', '--force', action='store_true', help="Don't prompt and assume yes")
    parser.add_argument('--allowKeyring', action='store_true', help="Allow the use of the users keyring")
    parser.add_argument('--priv', type=str, metavar="privKey", help="Private key to use")
    subparsers = parser.add_subparsers(help="Command", required=True, dest="cmd")
    handlers = {}
    handlers.update(addCmdCreate(subparsers))
    handlers.update(addCmdVerify(subparsers))
    handlers.update(addCmdPrint(subparsers))
    handlers.update(addCmdExport(subparsers))

    modifySubparsers = addModifySubparser(subparsers)
    handlers.update(addCmdAppend(modifySubparsers))
    handlers.update(addCmdAuthorize(modifySubparsers))
    handlers.update(addCmdRelease(modifySubparsers))

    args = parser.parse_args()

    handler = handlers.get(args.cmd)
    if handler is None:
        raise Exception("No handler for cmd {}".format(args.cmd))
    handler(args)

    exit(0)
    