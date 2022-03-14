*Authors Note: The motivation and problems described in this document are entirely derived from my own experience, I'm fully aware that there are likely inaccuracies or flat out wrong assumptions and am more than happy to have this pointed out to me or discussed.  
This is also the reason this document is written entirely from my own perspective.*

*At the moment this document is incomplete, more information along the same lines can be found in [user_stories.md](user_stories.md)*

# Motivation
The current way security disclosures are performed has some issues that I think are worth adressing.

While some issues are unavoidable and some amount of trust is always necessary.  
For example anybody with access to the information can always secretly hand it on to somebody else.

Other parts of the process can be improved howver.

I'll group the things that I think can be improved based on different interest groups.

## General Public

### No transparency
From the general publics point of view disclosure processes are entirely intransparent.  
Security issues are most often disclosed in secret and any information is only accessible after the disclosure process has concluded.
It is not uncommon for information to be deliberately withheld or obfuscated and to never be publicly released even in open source.

*For example  
"I respond with my work email, to which he is apprehensive because the domain name makes it obvious the patch is a security issue. I give my personal email instead, which he accepts."[^1]  
Or this patch for the recent mod_proxy SSRF in apache, giving no indication that it's security relevant at all [^2] [^3]*

[^1]: https://www.graplsecurity.com/post/iou-ring-exploiting-the-linux-kernel#toc-5

[^2]: https://svn.apache.org/viewvc?view=revision&revision=1892814

[^3]: https://firzen.de/building-a-poc-for-cve-2021-40438

This also means that from the perspective of an outside observer the parties involved in a disclosure have to be implicitly trusted.

### Researcher issues are General Public issues
Any of the issues affecting security researchers, will also cause problems for the general public.

If researchers are discouraged from disclosing an issue to a vendor for any reason it ultimately results in less secure systems, which affects everybody.

## Security Researcher
For security researchers there are several issues.  

### Disclosure overhead
Different vendors expect disclosures to be done in different ways since there is no real standard for this.  
[security.txt](https://securitytxt.org/) is addressing part of this, but is mainly standardizing where to find the relevant information, rather than the process following that.  
As a consequence the disclosure process is a lot more effort than simply finding and documenting a security issue.
For this reason it seems common (from private conversations I've had and my own experience) that especially low impact issues end up not being disclosed.  
That is because researchers can't justify spending the extra time required, especially if there is no bounty or other reward.

### Third party disclosure
Disclosing an issue through a third party is not an uncommon practice, since some vendors are painful to disclose to, have no or overly restrictive bounty programs or are litigious.  
In some cases companies run their bug bounty programs through third parties.  
In other cases the only way to see a financial return on their time spent on finding and documenting issues is to disclose to an independent third party like the ZDI.

However when disclosing through a third party the researcher has to trust that they will correctly handle the information and contact the vendor.

But this is not always guaranteed.

*For example  
§4b (4) of the German BSIG allows the agency to not disclosre an issue to a vendor.[^4]*

[^4]: https://www.gesetze-im-internet.de/bsig_2009/__4b.html*

*Authors Note: I only know of this German law in this case, if you have other (especially international) examples of laws or cases in which third parties have mishandled information I'd love to add more primary sources here*

 Should the third party act maliciously (or not in the researchers interest) it can be hard to do anything about it, especially if the original reason to disclose through the third party was anonymity, avoiding contact with the vendor or avoiding [full disclosure](https://en.wikipedia.org/wiki/Full_disclosure_(computer_security)).