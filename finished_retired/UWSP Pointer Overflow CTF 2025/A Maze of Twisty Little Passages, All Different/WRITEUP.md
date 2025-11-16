# A Maze of Twisty Little Passages, All Different - Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Misc
- **Difficulty**: Easy-Medium
- **Flag Format**: `poctf{uwsp_[THE HIDDEN MESSAGE]}`

## Challenge Description

A telemetry drone was sent into ruins beneath Knossos Station. The drone's mapping feed was corrupted, leaving only a movement log with position updates, turns, and dead ends. Our task is to reconstruct what the drone saw and find the message hidden in its path.

## Initial Analysis

The challenge provides:
- A telemetry log with 30 sectors
- Each sector starts at position (0,0) facing NORTH
- Movement commands include:
  - "Step forward" - moves one cell in current facing direction
  - "Turning left/right" - rotates 90 degrees
  - "Turning 180 degrees" - reverses direction
- Horizontal lines (sectors 4, 11, 17, 20) act as word separators

## Solution Approach

### 1. Parse the Telemetry Data

Created a Python script ([parse_telemetry.py](parse_telemetry.py)) to:
- Extract all 30 sectors from the README
- Parse movement commands from each sector
- Store them in a structured format

### 2. Simulate Drone Movement

For each sector:
- Track position starting at (0,0)
- Track facing direction (NORTH=0, EAST=1, SOUTH=2, WEST=3)
- Update position based on "Step forward" commands
- Update facing based on turn commands
- Record the complete path as a list of coordinates

### 3. Visualize the Paths

Generated visualizations in two formats:
- **ASCII art**: Simple text representation of each path
- **Matplotlib plot**: Detailed graphical visualization showing start/end points

Each path traces a block letter shape.

### 4. Identify the Letters

Read each sector's path to identify the letter it forms:
- Sectors 1-3: **ITS**
- Sector 4: *(separator)*
- Sectors 5-10: **ALWAYS**
- Sector 11: *(separator)*
- Sectors 12-16: **SUNNY**
- Sector 17: *(separator)*
- Sectors 18-19: **ON**
- Sector 20: *(separator)*
- Sectors 21-30: **TELEVISION**

### Challenges in Letter Identification

Some letters required careful analysis:
- **T vs L**: Both have similar shapes but T has horizontal bar on top
- **N vs C**: N shapes may appear as open rectangles in grid-based rendering
- **E vs S/5**: E has three horizontal bars
- **W vs M**: Sector 7 forms W (needed for "ALWAYS")
- **V vs T**: Sector 25 forms V (needed for "TELEVISION")

## Hidden Message

The complete message is: **"ITS ALWAYS SUNNY ON TELEVISION"**

This is a reference to the TV show *"It's Always Sunny in Philadelphia"*.

## Flag Conversion

The hidden message `its always sunny on television` must be converted to the proper flag format using l33tspeak:

**L33tspeak Mapping:**
- a → 4
- e → 3
- i → 1
- o → 0
- s → 5
- t → 7
- spaces → underscores

**Conversion:** `its always sunny on television` → `175_4lw4y5_5unny_0n_73l3v1510n`

**Final Flag:**
```
poctf{uwsp_175_4lw4y5_5unny_0n_73l3v1510n}
```

## Key Takeaways

1. Grid-based path tracing can be used to encode messages as letters
2. Each "sector" reset provides a clean slate for drawing individual letters
3. Visualization tools (both ASCII and graphical) are essential for pattern recognition
4. Context clues (like common phrases or pop culture references) help verify letter identifications
5. Some ambiguity in block letter rendering requires testing multiple interpretations

## Files Created

- `parse_telemetry.py` - Main script to parse and visualize the paths
- `sectors_visualization.png` - Graphical visualization of all 30 sectors
- `SOLUTION.md` - Quick solution summary
- `WRITEUP.md` - This detailed writeup
