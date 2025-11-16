# The Paper Trail - UNSOLVED

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: OSINT
- **Difficulty**: Medium

## Challenge Description
Find where a photo posted to Reddit ~8 years ago was taken. Near that location is a small town with a high school. Locate the 1940 yearbook and find a Senior with the first name matching the photographer. Convert their quote using the CTF's l33tspeak alphabet to get the flag.

## Progress Made

### 1. Photographer Identification ✓
- **Method**: Extracted EXIF metadata from OSINT200-1.jpg
- **Result**: Photographer is **Raymond K. Cunningham, Jr.**
- **Date**: September 9, 2017
- **Camera**: Canon EOS 5DS R

### 2. Photo Location ✓
- **Method**: Web search for the photographer and image
- **Result**: Photo titled "Sunrise on the Rails - Fairmount Illinois"
- **Location**: **Fairmount, Illinois** (Vermilion County)
- **Description**: Railroad tracks at sunset/sunrise

### 3. Flag Conversion Method ✓
- **Source**: flag_generator.py in the active folder
- **Format**: `poctf{uwsp_...}`
- **L33tspeak mapping**:
  - a → 4
  - e → 3
  - g → 6
  - i → 1
  - o → 0
  - s → 5
  - t → 7
  - spaces → underscores

## Assumptions Made

### Assumption 1: Catlin was the correct nearby town
- **Reasoning**: Catlin is a small town in Vermilion County near Fairmount
- **Evidence**: Catlin High School 1940 yearbook exists on Ancestry.com (46 images, 557 students)
- **Status**: UNVERIFIED - Could be wrong

### Assumption 2: "Nearby" means same county
- **Reasoning**: Searched within Vermilion County
- **Other candidates**: Georgetown, Danville, Oakwood (Fithian), Hoopeston
- **Status**: UNVERIFIED

### Assumption 3: Yearbook search functionality is accurate
- **Reasoning**: Searched for "ray" in Catlin 1940 yearbook on Ancestry
- **Result**: No matches found (search returned 2106 results which seems incorrect for 557 students)
- **Issue**: OCR might have failed, or search expanded beyond single yearbook
- **Status**: QUESTIONABLE

### Assumption 4: The yearbook is digitized and accessible
- **Reasoning**: Catlin 1940 yearbook listed on Ancestry.com
- **Issue**: May require manual page-by-page review rather than text search
- **Status**: PARTIALLY VERIFIED

### Assumption 5: Looking for first name "Raymond" only
- **Reasoning**: Challenge says "first name that matches the photographer"
- **Alternative**: Could be looking for full name "Raymond Cunningham"
- **Status**: BELIEVED CORRECT

## Next Steps for Solver

1. **Verify the correct town**:
   - Check other Vermilion County towns near Fairmount:
     - Georgetown High School, IL - 1940
     - Danville High School, IL - 1940
     - Oakwood High School (Fithian), IL - 1940
     - Hoopeston Area High School, IL - 1940

2. **Manual yearbook review**:
   - Browse Catlin 1940 yearbook pages manually (don't rely on search)
   - Focus on Senior class pages
   - Look for any student named Raymond [Last Name]

3. **Alternative search methods**:
   - Try searching for "Raymond" instead of "ray"
   - Try searching in other yearbook databases (E-Yearbook, Classmates, MyHeritage)
   - Contact local Vermilion County historical society

4. **Once Raymond is found**:
   - Note his exact quote from the yearbook page
   - Convert using l33tspeak: a→4, e→3, g→6, i→1, o→0, s→5, t→7
   - Format as: `poctf{uwsp_[converted_quote]}`

## Files in This Folder
- `OSINT200-1.jpg` - The railroad sunset photo with EXIF data
- `README.md` - Original challenge description
- `UNSOLVED.md` - This file

## Resources
- Ancestry.com - Has Catlin HS 1940 yearbook
- flag_generator.py - In ../active/ folder for flag conversion
- EXIF data in image shows photographer and date
