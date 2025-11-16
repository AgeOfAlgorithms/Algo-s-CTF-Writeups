# Map of Uncharted Waters - WRITEUP

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: OSINT
- **Difficulty**: medium-hard

## Challenge Description
The challenge describes a group of wealthy investors who:
1. Dreamed of creating their own paradise
2. Traveled to Thailand at coordinates 7°29'22.2"N 98°34'48.6"E
3. Were banished from Thailand
4. Bought a ship and decided to forever sail the seas
5. That venture also failed

The goal is to find the ship's original name.

## Solution

### Step 1: Identify the Project
The coordinates (7°29'22.2"N 98°34'48.6"E) and the story of wealthy investors trying to create their own paradise in Thailand points to the **seasteading movement** and specifically the **Ocean Builders** project.

In 2019, Ocean Builders (led by Elwartowski and others) built a floating "seastead" platform off the coast of Phuket, Thailand. The Thai Navy seized it, claiming it violated Thailand's sovereignty, and the operators faced serious charges including potential death penalty. This is the "banishment" mentioned in the challenge.

### Step 2: Find the Ship
After the Thailand incident failed, Ocean Builders pivoted to a new plan: purchasing a cruise ship to create a floating cryptocurrency utopia in international waters. The ship was named **MS Satoshi** (after Bitcoin's creator, Satoshi Nakamoto).

### Step 3: Research Ship History
MS Satoshi had a long history with multiple name changes:
- **Regal Princess** (1991-2007): Original name when launched by Princess Cruises
- **Pacific Dawn** (2007-2020): Second name under P&O Cruises Australia
- **MS Satoshi** (2020-2021): Ocean Builders' cryptocurrency cruise ship
- The project ultimately failed due to insurance issues and the ship was later sold and renamed Ambience in 2022

### Step 4: Determine the Original Name
The ship's **original name** was **Regal Princess** when it was first launched in 1991.

## Flag
Converting "Regal Princess" to the contest format with l33tspeak conversion:
- L33t mapping: a→4, e→3, g→6, i→1, o→0, s→5, t→7
- "Regal Princess" → "r364l_pr1nc355"

**`poctf{uwsp_r364l_pr1nc355}`**

## References
- Ocean Builders website and news articles about the Thailand incident
- Ship history databases showing the vessel's name changes
- News coverage of the MS Satoshi cryptocurrency cruise ship project
