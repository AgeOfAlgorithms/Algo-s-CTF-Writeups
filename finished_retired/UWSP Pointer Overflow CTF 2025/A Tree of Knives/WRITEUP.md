# A Tree of Knives - Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Reverse Engineering
- **Difficulty**: Easy
- **Flag**: `poctf{uwsp_pu7_7h3_bunny_b4ck_1n_7h3_b0x}`

## Solution

### Initial Analysis
The challenge provided a Windows PE32+ 64-bit executable (`rev100-3.exe`). The challenge description warned that the binary contains lots of "spaghetti code" as a distraction from what is otherwise a straightforward effort.

### Finding the Vulnerability
Since this was marked as an easy reverse engineering challenge, the first step was to run basic static analysis tools:

```bash
file rev100-3.exe
strings rev100-3.exe
```

### Exploitation
Running `strings` on the executable immediately revealed the flag stored in plaintext:

```bash
strings rev100-3.exe | grep -i poctf
```

Output:
```
poctf{uwsp_pu7_7h3_bunny_b4ck_1n_7h3_b0x}
```

### Additional Observations
The strings output also revealed several interesting function and variable names:
- `print_flag_if_ok` - Function that likely prints the flag
- `FLAG_PLAINTEXT` - Variable containing the flag
- `refer_to_flag` - Reference to flag data
- `enc_flag_buf` and `enc_flag_len` - Encrypted flag buffer (possibly unused)
- Messages: "No flag buffer present. Aborting." and "Well done. Flag: %s"

These suggest the program was designed with a verification mechanism that would print the flag upon success. However, since the flag is stored in plaintext in the binary, dynamic analysis or execution was unnecessary.

### Conclusion
This challenge demonstrates that even with obfuscated or complex code, basic static analysis techniques like `strings` can often reveal secrets stored directly in binaries. The challenge lived up to its "easy" rating - the distraction code didn't matter when the flag was hardcoded in plaintext.

**Time to solve**: < 2 minutes
**Tools used**: `strings`, `file`, `grep`
