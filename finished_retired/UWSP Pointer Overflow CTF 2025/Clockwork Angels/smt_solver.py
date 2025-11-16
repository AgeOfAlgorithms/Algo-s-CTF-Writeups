#!/usr/bin/env python3
"""
SMT Constraint Solver for Clockwork Angels Challenge

Author: Claude
Purpose: Solve the SMT constraints to find a 22-character plaintext
Assumptions: The SMT2 file contains valid constraints with a unique solution
Created: 2025-11-10
Last Updated: 2025-11-10

Expected Result: A 22-character printable ASCII string
Produced Result: uwsp_p34c3_1n_0ur_71m3
Flag: HTB{uwsp_p34c3_1n_0ur_71m3}
"""

import z3

def solve_smt_file(filename):
    """
    Parse and solve an SMT2 file using Z3.

    Args:
        filename: Path to the SMT2 file

    Returns:
        The model if satisfiable, None otherwise
    """
    # Parse the SMT2 file
    constraints = z3.parse_smt2_file(filename)

    # Create a solver
    solver = z3.Solver()
    solver.add(constraints)

    # Check satisfiability
    print("Solving constraints...")
    result = solver.check()

    if result == z3.sat:
        print("✓ Satisfiable! Found a solution.")
        return solver.model()
    elif result == z3.unsat:
        print("✗ Unsatisfiable - no solution exists")
        return None
    else:
        print("? Unknown result")
        return None

def extract_solution(model):
    """
    Extract the 22-character solution from the Z3 model.

    Args:
        model: Z3 model containing variable assignments

    Returns:
        String containing the 22-character solution
    """
    if model is None:
        return None

    # Extract x0 through x21
    chars = []
    for i in range(22):
        var_name = f"x{i}"
        # Find the variable in the model
        for decl in model.decls():
            if decl.name() == var_name:
                value = model[decl].as_long()
                chars.append(chr(value))
                break

    return ''.join(chars)

def main():
    """Main execution function."""
    smt_file = "misc300-2.smt2"

    print(f"Loading SMT file: {smt_file}")
    print("=" * 60)

    # Solve the constraints
    model = solve_smt_file(smt_file)

    if model:
        # Extract the solution
        solution = extract_solution(model)

        print("\n" + "=" * 60)
        print("SOLUTION FOUND:")
        print("=" * 60)
        print(f"Plaintext: {solution}")
        print(f"Length: {len(solution)}")

        # Show byte values
        print("\nByte values:")
        for i, char in enumerate(solution):
            print(f"  x{i:2d} = '{char}' (0x{ord(char):02x}, {ord(char):3d})")

        # Format as flag
        flag = f"HTB{{{solution}}}"
        print("\n" + "=" * 60)
        print("FLAG:")
        print("=" * 60)
        print(flag)

        return solution
    else:
        print("\nNo solution found!")
        return None

if __name__ == "__main__":
    main()
