# Digital Palimpsest - Writeup

**Challenge:** Digital Palimpsest
**Category:** Misc
**Difficulty:** Hard
**Platform:** UWSP Pointer Overflow CTF
**Flag:** `poctf{uwsp_y4p_y4p_y4p_y4p_y4p}`

## Challenge Description

The challenge provided three RAID-5 disk images that were captured after an "update" was performed in a hurry. The goal was to recover old data that had been overwritten by leveraging RAID-5 parity information.

**Given Information:**
- Three disk images: raid-d0.img, raid-d1.img, raid-d2.img
- RAID-5 with 3 members using left-symmetric parity rotation
- Chunk size: 64 KiB
- For stripe s: parity member p = s % 3; data members are (p+1)%3, (p+2)%3
- Some stripes are "torn" (inconsistent) - parity doesn't match current data

## Vulnerability Discovery

### Understanding RAID-5 Parity

In RAID-5, data is striped across multiple disks with parity information distributed among them. For a 3-disk RAID-5 array:
- Each stripe contains 2 data chunks and 1 parity chunk
- The parity is calculated as: `Parity = Data1 XOR Data2`
- The parity disk rotates with each stripe (left-symmetric)

### The Torn Write Concept

A "torn write" occurs when some disks are updated but others are not, leaving the array in an inconsistent state. In this challenge:
- The disks were updated with new data
- However, the parity information from before the update was retained
- This creates an inconsistency: `Parity_old ≠ Data_new1 XOR Data_new2`

### Key Insight

Since we know:
- `Parity_old = Data_old1 XOR Data_old2`
- And we have access to `Parity_old` and both new data chunks

We can recover old data using:
- `Data_old1 = Parity_old XOR Data_new2`
- `Data_old2 = Parity_old XOR Data_new1`

## Exploitation

### Step 1: Extract the Archive

```bash
unzip misc400.zip
```

This gave us three 16 MiB disk images, each containing 256 stripes (16 MiB / 64 KiB).

### Step 2: Implement RAID-5 Recovery Script

I created a Python script ([raid5_recovery.py](raid5_recovery.py)) that:

1. **Reads each stripe** from all three disks
2. **Determines parity distribution** using the left-symmetric rotation formula
3. **Checks parity consistency** by calculating expected parity and comparing with actual
4. **Recovers old data** when inconsistencies are found using XOR operations
5. **Extracts printable ASCII** to find the flag

### Step 3: Run the Recovery

```bash
python3 raid5_recovery.py
```

The script found 255 inconsistent stripes out of 255 total stripes analyzed.

### Step 4: Extract the Flag

In stripe 6, the recovered old data on disk 1 contained:

```
Dear future me; poctf{uwsp_y4p_y4p_y4p_y4p_y4p} -- parity remembers.
```

The message "parity remembers" is a beautiful reference to the fact that RAID-5 parity preserved the old data!

## Technical Details

### RAID-5 Stripe Layout

For this left-symmetric configuration:

| Stripe | Disk 0 | Disk 1 | Disk 2 |
|--------|--------|--------|--------|
| 0 | Parity | Data | Data |
| 1 | Data | Parity | Data |
| 2 | Data | Data | Parity |
| 3 | Parity | Data | Data |
| ... | ... | ... | ... |

### XOR Recovery Mathematics

The XOR operation has special properties:
- `A XOR B = C` implies `A = C XOR B` and `B = C XOR A`
- This makes data recovery possible when we have parity and one data chunk

## Lessons Learned

1. **RAID-5 parity can leak information** - Even after data is "deleted" or overwritten, parity information can reveal the old values
2. **Torn writes are a forensic goldmine** - Inconsistent updates can be exploited to recover previous states
3. **Digital palimpsests are real** - Just like ancient manuscripts that were scraped and reused, digital storage can retain "ghosts" of old data

## Flag

**`poctf{uwsp_y4p_y4p_y4p_y4p_y4p}`**
