## Challenge Name
Redirection Junction

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Web

## Difficulty
easy

## Challenge Description
The premise here is a little URL shortener that’s a touch too eager to help. Every link hands you off to another link, and another, and another. But often not the same way or under the same conditions. Your task is straightforward: follow the chain until you reach the final page and read the flag. The site will only reveal the flag when you arrive by the correct route.

Use your browser’s developer tools and inspect response bodies as well as headers. Simple text decoders (Base64, hex) and careful treatment of cookies and Referer headers are the intended tools.

Your target: https://web100-4.pointeroverflowctf.com
Good luck — follow the breadcrumbs, not just the Location header.

Update:
1) Not every step is a 30x response. Open developer tools and watch requests and responses: meta refreshes and tiny inline scripts may contain the next target inside the page body.

2) If you see a long, non-alphanumeric string in a page, try decoding it. A first pass with ordinary Base64 or URL-safe Base64 will often expose the next path component. Also preserve cookies between requests — one intermediate step will set a cookie you must carry forward.

When automating, either emulate what a browser sends or replay the browser’s artifacts: fetch intermediate HTML, decode client-side redirects yourself, and send the appropriate Referer header and cookies on subsequent requests. Simply using curl -L without decoding meta/js steps or without preserving Referer/cookies will not always reach the final page.
