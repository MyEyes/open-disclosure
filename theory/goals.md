# Goals
*Authors Note: These are the long term goals/aspirations of the project, some of these are certainly not fulfilled at the moment and at this point in time all of it is up for debate*

The goal of this project is to enable the security community to do security disclosures in a way that is:
* More transparent to the public
* Requires less trust between all parties
* Can be independently verified
* If an alteration or omission of data is detected it can be proven
* Allows researchers to remain anonymous
* Can guarantee that the vendor receives the information, even when disclosing through a third party.
* Provides a standardized way to exchange information

*The reason these things are desirable is outlined in [motivation.md](motivation.md).*  
*A way these things can be achieved is outlined in [concept.md](concept.md).*

To achieve this, the project consists of:  
* An open standard 
* A reference implementation
* Tooling to perform common operations

all of which are open source and will allow the security community to (independently and publicly) host, create, duplicate and verify disclosure processes.

# Short Term

In the short term the main goal is to get as many eyes as possible on this project to identify issues in the theoretical as well as practical aspects and to allow all interested parties to have a say.  
As it stands many aspects of the concept are not completely fleshed out and need to be more strictly defined.

*Authors Note: It is entirely possible that there are core issues in this concept that make it worthless, so those should be explored.*

Awareness and ideally adoption of a system like this is the most important short term goal.

# Long Term
If a system like this is widely adopted having multiple independent publicly hosted collections that mirror each other would make it easy to verify and almost impossible to even attempt to omit information.

This system makes it possible to have independent oversight that can impose fines or other penalties that are likely to hold up in court, because the process is public, independently verifiable, and violations of the process can be proven.  
In the same vain this could allow oversight of government agencies that are meant to facilitate the disclosure of security issues.

If the disclosure process shifts to simply uploading such a container to a public collection (which could then automatically notify the vendor), it will reduce the burden on independent researchers and will instead put the responsibility on vendors to seek out issues and initiate communication with the researcher if needed.  
Since independent researchers aren't guaranteed to get compensated for this effort, but a vendors salaried employees are, this seems like a more equitable system.