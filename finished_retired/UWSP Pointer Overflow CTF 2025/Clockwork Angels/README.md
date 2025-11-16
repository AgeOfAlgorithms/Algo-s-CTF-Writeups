## Challenge Name
Clockwork Angels

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Misc

## Difficulty
medium-hard

## Challenge Description
As an elective, I sometimes get to teach Game Hacking. It's easily one of my favorite to teach. We get to do cool things and learn a little about secure coding practices, logic, and client/server security along the way. If you're into this too then you've no doubt heard of Pwn Adventure 3. That's and intentionally vulnerable game from 2015's Ghost in the Shellcode CTF (and the inspiration for our game hacking category next year.) I have a series on YT running through it, but watch Live Overflow, he's better.

Each year I teach it, I challenge myself to find a new way to solve each challenge. In that games there's a puzzle that requires solving a 32b logic switch puzzle. The first year I mapped the logic gates out by hand in a spreadsheet. The second year I narrowed the key down to 16 bits and built a brute forcer. Third year, I used Z3 and THAT inspired this challenge.

In this challenge you’re given a system of constraints encoded for an SMT solver. Find any assignment that satisfies all constraints. The satisfying assignment encodes a 22-character plaintext. Convert the result to the flag by converting it using the contest rules.

[attachment](misc300-2.smt2)


