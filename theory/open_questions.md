# Open Questions
This document is meant to serve as a basis for discussion of parts of the theory that are not yet part of the concept. For that reason it is more of a stream of consciousness of pros and cons of the questions being discussed.

The document will necessarily reference concepts from the 

## Timegating
It is possible to explicitly add a kind of timegate to a container.

In an abstract sense this timegate is meant to guarantee the release of the containers shared key at some point in the future.

This release does not necessarily have to happen at a specific time, although that's a desirable property.
It should however guarantee (to some degree of certainty) when the shared key will be released AT THE EARLIEST, to prevent violating a disclosure deadline.

The main purpose is to guarantee that the shared key will eventually become public regardless of the actions of any of the containers authorized parties.