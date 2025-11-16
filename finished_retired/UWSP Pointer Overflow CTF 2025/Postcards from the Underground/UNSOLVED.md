# Postcards from the Underground - UNSOLVED

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF (HackTheBox)
- **Category**: OSINT
- **Difficulty**: Easy
- **Status**: UNSOLVED

## Challenge Description
Find the defunct Internet Service Provider (ISP) for RELIAGRAPHICS Engineering Limited, a UK metal fabrication company. The ISP must:
- Be defunct/no longer in business
- Have offered .net email services
- Submit answer in format: `poctf{uwsp_ISPNAME}` where ISPNAME is in leet speak

## What We Found

### Company Information
- **Name**: RELIAGRAPHICS Engineering Limited
- **Type**: Metal fabrication company
- **Status**: Dissolved 2019 (Company No. 04619028)
- **Location**: Unit 11 Bilton Road, Manor Road, Erith, Kent DA8 2AN
- **Operations**: 30+ years experience, work for London Underground

### Website Investigation
- **Domain**: reliagraphics.co.uk
- **Archived**: 8 snapshots from 2008-2014 on Wayback Machine
- **Email Domain**: @reliagraphics.com (not @reliagraphics.co.uk)
- **Website Designer**: WebCreation UK (also provided hosting services)
- **Current DNS**: Points to IONOS/1&1 servers

### Email Addresses Found
All used @reliagraphics.com domain:
- enquiries@reliagraphics.com
- gordon@reliagraphics.com
- steve@reliagraphics.com
- richard@reliagraphics.com
- matt@reliagraphics.com
- glenn@reliagraphics.com

### MD5 Hash Clarification
The provided hash `33FB2D694B51A504D7CFF475BB6D461A` is the MD5 of OSINT100-1.jpg (for file integrity), NOT the answer verification hash.

## ISPs Tested (All Failed)

### Major Defunct UK ISPs with .net
- Freeserve (fr33s3rv3, freeserve)
- Demon Internet (d3m0n, demon)
- Pipex (p1p3x, pipex)
- Tiscali (715c4l1, tiscali)
- Blueyonder (blu3y0nd3r, blueyonder)
- NTL (n7l, ntl)
- Telewest (73l3w357, telewest)
- LineOne (l1n30n3, lineone)
- Compuserve (c0mpu53rv3, compuserve)
- World Online (w0rld0nl1n3, worldonline)
- Virgin Net (v1rg1nn37, virginnet)
- Supanet (5up4n37, supanet)
- Eclipse (3cl1p53, eclipse)
- Force9 (f0rc39, force9)
- UK Online (uk0nl1n3, ukonline)
- AOL (40l, aol)

### Hosting Providers
- 1&1 / 1and1 / 1und1 (14nd1, 1&nd1)
- IONOS
- WebCreation UK

### Variations Tested
- With/without underscores after "uwsp"
- Standard leet speak (a=4, e=3, i=1, o=0, s=5, t=7)
- Extended leet speak
- Various capitalizations
- With/without spaces

**Total Attempts**: 676+ combinations tested

## What We Missed

The answer likely requires:
1. **More specific OSINT**: Perhaps examining WHOIS history, DNS history archives, or email headers from archived pages
2. **Alternative sources**: Looking at Companies House filings, invoices, or business documentation
3. **Less obvious ISP**: May be a smaller, regional UK ISP that we didn't consider
4. **Different format**: The flag format might be different than expected (though we tested many variations)
5. **Historical context**: The ISP might have had a different name or branding at the time

## Tools Used
- Wayback Machine (web.archive.org)
- DNS lookups (dig, nslookup)
- Playwright browser automation for archived sites
- Python for systematic flag generation and testing
- Companies House search for business records

## Files in This Directory
- `OSINT100-1.jpg` - Main challenge image (London Underground mirror with RELIAGRAPHICS label)
- `OSINT100-Hint.jpg` - Close-up of the RELIAGRAPHICS label
- `README.md` - Original challenge description
- `UNSOLVED.md` - This summary document

## Recommendations for Future Attempts

1. **Deep dive into DNS history**: Use services like SecurityTrails, DNSHistory, or ViewDNS to find historical DNS records
2. **Check email headers**: If any archived emails or contact forms exist, examine headers for ISP clues
3. **Business records**: Look through Companies House documents for ISP mentions
4. **Web hosting forums**: Search for mentions of RELIAGRAPHICS on web hosting/design forums from 2007-2008
5. **Contact challenge author**: The answer might require knowledge of a very specific/regional UK ISP
6. **Alternative leet speak**: Try other leet speak variations or character substitutions

## Lessons Learned
- Don't assume MD5 hash is for answer verification without testing
- Exhaustive testing isn't always the solution - sometimes need a different approach
- OSINT challenges may require very specific historical knowledge
- The "obvious" answer (current DNS hosting) may not be the correct historical answer
