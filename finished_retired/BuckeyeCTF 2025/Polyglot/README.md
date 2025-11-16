## Challenge Name
Monoglot, Diglot, Triglot, etc.

## Platform
BuckeyeCTF 2025

## Category
polyglot

## Difficulty
multiple

## Challenge Description
The Chimera is many beasts in one. Craft a single executable that does the same operations on as many architectures as possible (each additional one reveals a flag)

Connection: `ncat --ssl 381KwDeUheCsUMjHJ.polyglot.challs.pwnoh.io 1337`

## Solution Status
**PARTIAL SOLUTION: 2/10 architectures (Diglot)**

See [WRITEUP.md](WRITEUP.md) for complete details.

## Files
- `diglot_solution.py` - Working x86/x86_64 polyglot shellcode
- `WRITEUP.md` - Detailed writeup and analysis
- `README.md` - This file

## Flags Obtained
1. Monoglot: `bctf{a_good_start_4fc9c43c0d95}`
2. Diglot: `bctf{now_you_are_bilingual_d9731b3bf6bf}`

## Usage
```bash
conda activate ctf
python3 diglot_solution.py
```
