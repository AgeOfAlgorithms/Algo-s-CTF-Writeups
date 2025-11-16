# CTF Challenge Collection 2025

A curated collection of Capture The Flag (CTF) challenge writeups and solutions from various competitions. Challenges are solved by AgeOfAlgorithms in collaboration with AI (AI does 90%).

## Repository Structure

```
Collection2025/
├── finished_retired/          # Completed challenges from past CTFs
│   ├── BuckeyeCTF 2025/
│   └── UWSP Pointer Overflow CTF 2025/
├── finished_active/           # Completed challenges from ongoing CTFs (Not included in repo)
└── in_progress/               # Challenges currently being worked on (Not included in repo)
```

## Challenge Format

Each challenge directory typically contains:
- `README.md` - Challenge description, platform, category, difficulty
- `WRITEUP.md` - Detailed solution and methodology (when available)
- OR `UNSOLVED.md` - Detailed steps taken an assumptions made
- Challenge files - Binaries, source code, pcaps, images, etc.
- Solution scripts - Exploits, decoders, analysis tools

## Usage

### Prerequisites
Common tools used across challenges:
- Python 3.x with various libraries (pwntools, cryptography, etc.)
- Binary analysis: `gdb`, `ghidra`
- Network analysis: `wireshark`, `tshark`, `netcat`
- Cryptography: `SageMath`, `OpenSSL`
- Steganography: `steghide`, `stegsolve`, `zsteg`
- Web tools: `curl`, `browser dev tools`

### Running Solutions

Navigate to the specific challenge directory and follow the writeup instructions. Most exploits and scripts include documentation headers with:
- Author
- Purpose
- Assumptions
- Expected results
- Actual results (updated after execution)

## Notes

- Challenges in `finished_retired/` are from completed CTFs and safe to share publicly
- Challenges in `finished_active/` are not shared.
- Some challenges require external files or services that are no longer available
- Large binary files are excluded from the repository (see [.gitignore](.gitignore))

## License

This repository contains educational CTF challenge solutions. All challenges are property of their respective CTF organizers. Solutions and writeups are for educational purposes only.
