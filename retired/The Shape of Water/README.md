## Challenge Name
The Shape of Water

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Web

## Difficulty
medium-hard

## Challenge Description
The Lacustrine Conservancy is a small aquarium and watershed education non-profit. Their developers built a preview service to test theme settings and publish monthly newsletters. Unfortunately, they didn’t pay much attention to how configuration data is handled during the build process. You’ve been asked to conduct a security assessment. The server merges user-supplied JSON into its global configuration and then uses that configuration during the newsletter build.

Endpoints
POST /api/settings — submit JSON to merge into the server’s configuration.
GET /api/build — generates the current newsletter preview (and processes configuration).
GET /api/debug/cfg — shows the current configuration’s own properties.
GET /api/logs — shows build and settings logs.
POST /api/reset — clears current settings and logs.
GET /api/version — returns version information.
Static files are served from /public (e.g., GET /newsletter.html).


Retrieve the contents of /flag.txt from the server. You cannot fetch it directly — you’ll need to figure out how to influence the build process to make it accessible.

Your Target: [Après Nous, le Déluge](https://web300-2.pointeroverflowctf.com/)
DNS may not be available for this instance. If the challenge hostname does not resolve, use the public IP 34.9.14.80 and send the Host header web300-2.pointeroverflowctf.com.
