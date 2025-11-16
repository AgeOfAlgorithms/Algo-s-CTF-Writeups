## Challenge Name
Digital Palimpsest

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Misc

## Difficulty
hard

## Challenge Description
A palimpsest is a manuscript that’s been scraped and written over—but if you squnit you can see the old words come through. This is a digital version of that. Best as I could manage, anyway. You’re handed three raw device captures from a tiny lab array that was “updated” in a hurry. The drives were imaged after the update, not before. Let's see if we can uncover some secrets, shall we?

If parity math left any ghosts behind, you should be able to resurrect the overwritten bytes.

* Files: raid-d0.img, raid-d1.img, raid-d2.img
* Level: RAID-5, 3 members, left-symmetric parity rotation (for stripe s: parity member p = s % 3; data members in logical order are (p+1)%3, (p+2)%3)
* Chunk size: 64 KiB
* Images are raw stripes only (no partitions, no filesystem)
* Some stripes are intentionally torn (inconsistent); the plaintext line does not appear contiguously in any single member file

[attachment](misc400)
