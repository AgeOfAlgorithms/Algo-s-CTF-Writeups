# Clockwork Angels - CTF Writeup

**Category:** Misc
**Difficulty:** Medium-Hard
**Flag:** `HTB{uwsp_p34c3_1n_0ur_71m3}`

## Challenge Description

The challenge presents an SMT (Satisfiability Modulo Theories) solver puzzle inspired by solving logic gate puzzles in Pwn Adventure 3 using Z3. We're given a file `misc300-2.smt2` containing constraints that encode a 22-character plaintext message.

## Vulnerability Analysis

This isn't a traditional "vulnerability" challenge but rather a constraint satisfaction problem. The challenge lies in solving a system of mathematical constraints to find the unique 22-character ASCII string that satisfies all conditions.

### Constraint Overview

The SMT2 file defines:
- 22 variables (x0 through x21) representing bytes
- Each byte must be printable ASCII (0x20 to 0x7e)
- Multiple constraint types:
  - **Pair sums:** e.g., x0 + x1 = 236
  - **XOR constraints:** e.g., x0 XOR x1 = 0x02
  - **Fixed values:** x4, x10, x13, x17 = '_' (underscore)
  - **Equality relations:** e.g., x3 = x5 (both 'p')
  - **Character relationships:** e.g., x1 = x0 + 2 (w = u + 2)
  - **Triple block sums:** e.g., x0 + x1 + x2 = 351
  - **Global checksums:** Sum of all bytes = 1910

## Solution Approach

### Step 1: Understanding SMT Solvers

SMT solvers like Z3 are tools designed to determine if a given formula is satisfiable and, if so, provide a model (assignment of values) that satisfies all constraints.

### Step 2: Using Z3

Instead of manually solving the complex system of constraints, we can use Z3's built-in SMT2 file parser:

```python
import z3

# Parse the SMT2 file
constraints = z3.parse_smt2_file("misc300-2.smt2")

# Create solver and add constraints
solver = z3.Solver()
solver.add(constraints)

# Check satisfiability
if solver.check() == z3.sat:
    model = solver.model()
    # Extract solution...
```

### Step 3: Extracting the Solution

The solver finds values for x0 through x21 that satisfy all constraints:

```
x0='u', x1='w', x2='s', x3='p', x4='_', x5='p',
x6='3', x7='4', x8='c', x9='3', x10='_', x11='1',
x12='n', x13='_', x14='0', x15='u', x16='r', x17='_',
x18='7', x19='1', x20='m', x21='3'
```

Concatenated: **uwsp_p34c3_1n_0ur_71m3**

### Step 4: Flag Format

Converting to the standard CTF flag format: `HTB{uwsp_p34c3_1n_0ur_71m3}`

## Key Insights

1. **Recognizing the Problem Type:** Understanding that this is an SMT solver challenge is crucial. The .smt2 extension and challenge description mentioning Z3 are key hints.

2. **Tool Selection:** Z3 is the industry-standard SMT solver and has excellent Python bindings, making it ideal for this task.

3. **Automated Solving:** Rather than attempting to manually solve the constraints (which would be extremely tedious and error-prone), leveraging Z3's built-in SMT2 parser provides an elegant solution.

4. **Leetspeak Message:** The decoded message "uwsp peace in our time" uses leetspeak substitutions (3→e, 4→a, 1→i, 7→t, 0→o).

## Tools Used

- **Z3 Theorem Prover:** SMT solver with Python bindings
- **Python 3:** Script automation

## References

- [Z3 Theorem Prover](https://github.com/Z3Prover/z3)
- [SMT-LIB Standard](https://smtlib.cs.uiowa.edu/)
- [Pwn Adventure 3](https://www.pwnadventure.com/)

## Files

- `misc300-2.smt2` - Challenge file with SMT constraints
- `smt_solver.py` - Python solution script
- `WRITEUP.md` - This writeup
