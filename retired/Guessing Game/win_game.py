#!/usr/bin/env python3
"""
Author: Claude
Purpose: Win the Guessing Game using binary search
Created: 2025-11-09
Last Updated: 2025-11-09
Expected Result: Win the game and reach the name input prompt
Produced Result: Successfully wins the game in 7-9 guesses

Usage: python3 win_game.py [max_number]
"""

from pwn import *
import sys

context.log_level = 'info'

def binary_search_win(max_num=100):
    """Win the guessing game using binary search"""
    io = remote('guessing-game.challs.pwnoh.io', 1337, ssl=True)

    # Send max number
    io.recvuntil(b'Enter a max number:')
    io.sendline(str(max_num).encode())
    log.info(f"Set max number to: {max_num}")

    # Binary search for the number
    low, high = 0, max_num
    guess_count = 0

    while low <= high and guess_count < 10:
        mid = (low + high) // 2
        guess_count += 1

        io.recvuntil(b'Enter a guess:')
        io.sendline(str(mid).encode())
        log.info(f"Guess {guess_count}: {mid}")

        response = io.recvline().decode().strip()

        if "got it" in response.lower():
            log.success(f"Found the number: {mid} in {guess_count} guesses!")
            break
        elif "Too low" in response:
            low = mid + 1
        elif "Too high" in response:
            high = mid - 1

    return io

def quick_win():
    """Win instantly using the max=0 shortcut"""
    io = remote('guessing-game.challs.pwnoh.io', 1337, ssl=True)

    io.recvuntil(b'Enter a max number:')
    io.sendline(b'0')
    log.info("Using quick win: max=0")

    io.recvuntil(b'Enter a guess:')
    io.sendline(b'0')
    log.info("Guessing: 0")

    log.success("Quick win successful!")
    return io

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        io = quick_win()
    else:
        max_num = int(sys.argv[1]) if len(sys.argv) > 1 else 100
        io = binary_search_win(max_num)

    # Now at the name prompt
    io.recvuntil(b'Enter your name for the leaderboard:')
    log.info("Reached leaderboard name prompt")

    # Send a safe name
    name = input("Enter name (max 10 bytes safe): ")
    io.sendline(name.encode())

    # Get final response
    response = io.recvall(timeout=2)
    print(response.decode())

    io.close()

if __name__ == "__main__":
    main()
