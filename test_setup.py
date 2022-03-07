# This file mainly exists as an example for how to use the library rather than the CLI tool
# And as a quick way to test functionality
# I'll probably remove it when I implement unit tests for the library
# Also since I've deleted the pub and priv keys loaded here it won't currently work

import opendisclosure as od
import pgpy
import opendisclosure.container.io.containerJSON as odjson
pubkey = pgpy.PGPKey.from_file("test/key_pub")[0]
privkey = pgpy.PGPKey.from_file("test/key_priv")[0]
ci = od.ContainerCreationInfo(pubkey)

c = od.Container(ci, privkey)
testEntry = od.ContainerEntry(od.ContainerEntryType.TEXT, creatorId=0, title="Test Entry", data="This is some test data for this entry", encrypted=False)
c.appendEntry(testEntry, privkey)
testEntry2 = od.ContainerEntry(od.ContainerEntryType.TEXT, creatorId=0, title="Test Entry2", data="This is some test data for an encrypted entry", encrypted=True, cipher=c.GetCipher())
c.appendEntry(testEntry2, privkey)
c.authorize(pubkey,privkey)

odjson.ContainerJSON.ContainerToJSONFile(c, "test/testContainer.json")

c2 = odjson.ContainerJSON.JsonFileToContainer("test/testContainer.json")
odjson.ContainerJSON.ContainerToJSONFile(c2, "test/testContainer2.json")
c2.release(privkey)
odjson.ContainerJSON.ContainerToJSONFile(c2, "test/testContainer3.json")