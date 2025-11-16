## Challenge Name
Mouth of Sauron

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Web

## Difficulty
hard

## Challenge Description
Welcome to the Palantír Press Office — All-Seeing Eye Community Showcase!

We curate community artwork and generate magazine-quality thumbnails from submitted SVG files. For editorial fidelity we preserve many vector primitives — including filters — while removing scripting and obvious executable content.

Guidelines:
Allowed format: SVG only (≤ 512 KB)
Thumbnails: server-side rendered to 900×600 PNG (may include a faint watermark)
Privacy: Submissions are private by default. After upload you are redirected to an asset page: /asset/?t= — that token is the only way to view your rendered asset.
Compatibility: The renderer preserves filter primitives (e.g. , , ). Visual effects that use filters may still render in the thumbnail.

The target & source of truth:
Internal design/asset host (only accessible from the renderer): barad-dur:31337
Flag image (internal): /flag.png on that host.
Flag format: poctf{...} — the flag is rendered into this PNG.
Important: You cannot reach barad-dur directly from your own browser — only the server-side renderer can.

Your Target: [Web400](https://web400.pointeroverflowctf.com/)
