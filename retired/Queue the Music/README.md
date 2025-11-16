## Challenge Name
Queue the Music

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
medium

## Challenge Description
There once was a time when I kept my media library on a home server and connected endpoints to each TV around the house. Worked great, but times have changed. Now the servers are up in the cloud and all the TVs are smart. Such is life, but now I need to redo all my media again. I decided to just create my own distribution system using playlists.

Look at https://exp200-1.pointeroverflowctf.com and you can see what I'm up to. I have a web service that turns uploaded tracks into a public playlist. Still working out the bugs. Talk to anyone, and they'll tell you how racy these things can get. Check it out, and use it if you like.

The flag will not require conversion for this challenge.

Base URL: https://exp200-1.pointeroverflowctf.com
Target: /flag/flag.txt
Health check: GET /health → ok
POST /session → {"sid":""} — get a session token (SID).
POST /upload (sid, content) — writes your track.txt.
POST /queue (sid) — read your track and append it to the public playlist.
GET /playlist — shows current playlist.
GET robots.txt

[Source](https://pointeroverflowctf.com/static/exp200-1.c)

Anything else will require some digging.
