# Candidate Flags for Unsolved Challenges

**L33tspeak Mapping:** `a→4, e→3, g→6, i→1, o→0, s→5, t→7`

---

## Room with a View

### High Priority Candidates

Based on hearse club research:

1. **`poctf{uwsp_6r4v3516h75}`** - "gravesights" (Grave Sights Hearse Club, Wisconsin)
2. **`poctf{uwsp_6r4v3_516h75}`** - "grave sights" (with space)
3. **`poctf{uwsp_p3rrycl43y5}`** - "perry claeys" (President of Grave Sights, aka "DrDeath")
4. **`poctf{uwsp_drd347h}`** - "drdeath" (Perry Claeys' nickname)
5. **`poctf{uwsp_h4rdc0r3h34r53}`** - "hardcore hearse" (Illinois club near Wisconsin)

### Medium Priority

6. **`poctf{uwsp_nh44}`** - "nhaa" (National Hearse & Ambulance Association) - ALREADY TESTED, REJECTED
7. **`poctf{uwsp_70d13f0r}`** - "to die for" (variation of plate "TO DIE 4")

### Notes
- License plate is "TO DIE 4" on a hearse
- Looking for "very unusual club" leader
- Grave Sights is Wisconsin-based and has unusual structure (free membership, no restrictions)
- Perry Claeys/DrDeath is the president

---

## Postcards from the Underground

### UK ISP Candidates (Defunct, with .net services)

All in proper l33tspeak format:

1. **`poctf{uwsp_fr3353rv3}`** - "freeserve" (Major UK ISP, defunct 2007)
2. **`poctf{uwsp_d3m0n}`** - "demon" (Demon Internet, defunct 2007)
3. **`poctf{uwsp_d3m0n_1n73rn37}`** - "demon internet" (full name)
4. **`poctf{uwsp_p1p3x}`** - "pipex" (Defunct UK ISP)
5. **`poctf{uwsp_715c4l1}`** - "tiscali" (Bought Pipex, later acquired)
6. **`poctf{uwsp_blu3y0nd3r}`** - "blueyonder" (Cable ISP, merged)
7. **`poctf{uwsp_n7l}`** - "ntl" (Merged with Telewest)
8. **`poctf{uwsp_l1n30n3}`** - "lineone" (Defunct UK ISP)
9. **`poctf{uwsp_c0mpu53rv3}`** - "compuserve" (UK operations)
10. **`poctf{uwsp_v1r61nn37}`** - "virginnet" (Virgin's ISP service)
11. **`poctf{uwsp_v1r61n_n37}`** - "virgin net" (with space)

### Hosting Providers (Less likely but possible)

12. **`poctf{uwsp_14nd1}`** - "1and1" (Current DNS host for reliagraphics.com)
13. **`poctf{uwsp_10n05}`** - "ionos" (1&1's rebranded name)
14. **`poctf{uwsp_w3bcr34710n}`** - "webcreation" (Website designer/host mentioned)

### Notes
- Looking for defunct ISP that provided .net email for RELIAGRAPHICS Engineering
- Company was dissolved in 2019
- Website active 2008-2014
- All email addresses used @reliagraphics.com domain

---

## Key Differences from Previous Attempts

**The g→6 mapping was missing!** Previous attempts didn't convert 'g' to '6', which would have invalidated flags like:
- "grave sights" → should be `6r4v3_516h75` not `gr4v3_516h75`
- "virgin net" → should be `v1r61n_n37` not `v1rg1n_n37`

This correction may make previously rejected answers work now.

---

## How to Use This Document

1. Try all **High Priority** flags for Room with a View first
2. For Postcards, try the major defunct UK ISPs (Freeserve, Demon, Pipex) first
3. Remember: Flags are **case insensitive**
4. All flags follow format: `poctf{uwsp_...}`
5. No spaces (replaced with underscores) unless specifically testing the variation
