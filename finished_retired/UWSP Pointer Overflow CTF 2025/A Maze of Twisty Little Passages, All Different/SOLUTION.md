## Solution

### Challenge Analysis

The challenge provides telemetry data from a drone that maps paths through a maze. Each of the 30 sectors traces a path that forms a letter when visualized.

### Approach

1. Parse the telemetry log to extract movement commands for each sector
2. Simulate the drone's path by tracking position and facing direction
3. Visualize each path to identify the letter it traces
4. Read the letters in sequence to reveal the hidden message

### Key Insights

- Each sector starts at position (0,0) facing NORTH
- Movements include: "Step forward", "Turning left/right", "Turning 180 degrees"
- The horizontal lines between some sectors are separators (spaces)
- The path traced by the drone in each sector forms a block letter

### Hidden Message

The 30 sectors spell out: **"ITS ALWAYS SUNNY ON TELEVISION"**

(This is a reference to the TV show "It's Always Sunny in Philadelphia")

### Hidden Message (Plaintext)

`its always sunny on television`

### Flag (with l33tspeak conversion)

The flag uses l33tspeak conversion rules:
- a → 4, e → 3, i → 1, o → 0, s → 5, t → 7
- spaces → underscores

```
poctf{uwsp_175_4lw4y5_5unny_0n_73l3v1510n}
```

### Notes on Letter Identification

Some letters required careful analysis:
- Sectors with 'T' shapes (horizontal bar on top, vertical stem) vs 'L' shapes
- Sectors with 'N' shapes that may appear as 'C' or 'U' depending on rendering
- Sectors with 'E' shapes that could resemble '5' or 'S'
- Sector 7 forms a 'W' (for ALWAYS) rather than an 'M'
- Sector 25 forms a 'V' (for TELEVISION)

The message with word separators: `ITS-ALWAYS-SUNNY-ON-TELEVISION`
