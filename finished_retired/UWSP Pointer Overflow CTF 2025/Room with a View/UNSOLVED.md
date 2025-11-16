# Room with a View - Unsuccessful Attempt

**Challenge:** Room with a View
**Category:** OSINT
**Difficulty:** Easy
**Platform:** UWSP Pointer Overflow CTF
**Status:** UNSOLVED

## Challenge Description

Given an image of a hearse with license plate "TO DIE 4" and asked to identify the "very unusual club" that the driver leads. The flag format is `poctf{uwsp_ _ _ }`.

## Assumptions Made

### Assumption 1: Wisconsin Geography
**Assumption:** Since the challenge is from UWSP (University of Wisconsin Stevens Point), the vehicle must be from Wisconsin.
**Reasoning:** Geographic context from the challenge source.
**Verification Attempted:** Searched for Wisconsin-specific hearse clubs and tried to access Wisconsin DMV license plate registry.
**Outcome:** Could not verify plate ownership through public records.

### Assumption 2: Club Leader Must Be Identifiable
**Assumption:** The person with the "TO DIE 4" plate is the leader of a hearse club that can be found through web research.
**Attempted Approaches:**
- Searched for hearse clubs in Wisconsin (Grave Sights Hearse Club)
- Looked for national organizations (NHAA, PCS, Denver Hearse Association)
- Tried to find the specific vehicle owner through license plate lookups
**Outcome:** Found multiple clubs but couldn't definitively link the plate to a specific owner.

### Assumption 3: "Very Unusual" Refers to Club Structure
**Assumption:** The phrase "very unusual club" refers to organizational structure rather than just embracing dark humor.
**Clubs Investigated:**
1. **National Hearse & Ambulance Association (NHAA)** - Unusual because it's a "club of clubs" with no dues
2. **Grave Sights Hearse Club** - Unusual because it's free membership with no restrictions
3. **Professional Car Society (PCS)** - Traditional structure but prohibits dark humor (ruled out)

**Flags Attempted:**
- `poctf{uwsp_nhaa}` - REJECTED
- `poctf{uwsp_gravesights}` - NOT TESTED
- `poctf{uwsp_grave_sights}` - NOT TESTED

### Assumption 4: License Plate Registry Would Be Accessible
**Assumption:** Wisconsin DMV would have a publicly accessible license plate lookup tool.
**Attempted:**
- https://wisconsindot.gov/Pages/online-srvcs/other-servs/pp-search.aspx (connection refused)
- https://trust.dot.state.wi.us/ppup/searchPlate.do (timeout)
- Various third-party plate lookup services (restricted by DPPA)
**Outcome:** Could not access the registry to identify the vehicle owner.

### Assumption 5: The Image Contains All Necessary Clues
**Assumption:** The "TO DIE 4" plate and hearse vehicle type are the only visual clues needed.
**Other Details Observed:**
- BMO bank sign in background
- Traffic setting
- Skeleton decorations in rear window
- No visible location-specific landmarks
**Outcome:** No additional identifying information found in the image.

## Research Findings

### Hearse Clubs Identified

1. **Professional Car Society (PCS)**
   - Founded 1976
   - Prohibits morbid displays and dark humor
   - Does NOT match "TO DIE 4" gallows humor theme

2. **National Hearse & Ambulance Association (NHAA)**
   - Founded by Alex Lohman, Zachary Byron Helm, Chris DiGanci
   - "Club of clubs" with minimal rules
   - Unusual structure but no direct connection to plate

3. **Grave Sights Hearse Club**
   - Wisconsin/Kenosha based
   - President: Perry Claeys ("DrDeath")
   - Vice President: Matt Dunham
   - Free membership, no restrictions
   - Archived website at oocities.org/gravemenu/1.html

4. **Hardcore Hearse Club**
   - Illinois-based (near Wisconsin)
   - President: Darlene Daniels
   - Active club with annual shows

5. **Denver Hearse Association**
   - Colorado-based
   - Founded by Zachary Byron Helm
   - Not geographically relevant

6. **De Come Pose**
   - Hearse photo booth service
   - Facebook page mentions "TO DIE 4" plates
   - Based in Carson City, Nevada (NOT Wisconsin)

## Critical Missing Information

1. **Vehicle Owner Identity**: Could not determine who owns the "TO DIE 4" hearse
2. **Direct Club Linkage**: No definitive connection between the plate and any specific club leader
3. **Geographic Verification**: BMO bank location and other background details not analyzed for location
4. **License Plate Registry**: Unable to access Wisconsin DMV records

## Tools Used

- exiftool (image metadata analysis)
- Web search engines
- Browser automation (Playwright)
- Archived website databases (oocities.org)

## Next Steps for Future Attempts

1. **Find the actual vehicle owner** - This appears to be the critical missing step
2. Use Wisconsin DMV resources if accessible (may require different access method)
3. Reverse image search the specific photo to find where it was originally posted
4. Check if BMO bank locations can narrow down geographic area
5. Look for social media posts featuring this specific hearse
6. Search for news articles or blog posts about hearse owners in Wisconsin
7. Consider that the plate might not be Wisconsin despite UWSP context

## Lessons Learned

1. OSINT challenges often require finding a specific person, not just organizations
2. Public records databases may have access restrictions that prevent automated lookups
3. Making assumptions based on geographic context (UWSP = Wisconsin) may be misleading
4. The phrase "leader of a club" likely means a specific named individual, not just a club name
5. License plate registry lookup is mentioned as a key step but wasn't successfully completed

## Files in This Directory

- `OSINT100-2.jpg` - Original challenge image
- `README.md` - Challenge description
- `ATTEMPT.md` - This file documenting unsuccessful attempt
