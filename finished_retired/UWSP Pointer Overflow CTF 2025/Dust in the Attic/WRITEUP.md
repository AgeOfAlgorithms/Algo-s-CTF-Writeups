# Dust in the Attic - Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Forensics
- **Difficulty**: Easy-Medium
- **Flag**: `poctf{uwsp_7humbn41l5_n3v3r_f0r637}`

## Challenge Description
> I spent some time cleaning out the attic last spring. Long overdue. I took a few pictures while I was up there. I've been looking for an excuse to use the camera more. Hope you like them!

## Initial Analysis

The challenge provided a 7z archive (`FOR200-1.7z`) containing:
- 4 JPG images: IMG_2010, IMG_2011, IMG_2012, and IMG_2014
- A Windows thumbcache database: `thumbcache_96.db`

**Key Observation**: There's a missing image in the sequence - IMG_2013 is not present. This, combined with the thumbcache database (which stores thumbnail previews of images), suggested the challenge might involve recovering deleted image data.

## Vulnerability Discovered

The vulnerability was improper data sanitization in the image metadata. The challenge creator embedded the flag in the EXIF metadata of one of the images.

## Exploitation

Using `exiftool` to examine the metadata of all JPG files:

```bash
exiftool *.jpg
```

In the EXIF data of `IMG_2010 attic.jpg`, the XP Comment field contained the flag:

```
XP Comment: poctf{uwsp_7humbn41l5_n3v3r_f0r637}
```

The flag translates to "thumbnails never forget" in leetspeak, which is a clever reference to Windows thumbnail caches that can retain thumbnails of images even after the original files are deleted.

## Solution Summary

1. Extract the 7z archive
2. Run `exiftool` on all JPG images
3. Locate the flag in the XP Comment field of IMG_2010 attic.jpg

## Key Takeaway

Always examine EXIF metadata when dealing with image forensics challenges. Metadata fields like XP Comment, Image Description, and others can contain hidden information or clues. The "missing" IMG_2013 and the thumbcache database were red herrings designed to misdirect solvers toward more complex thumbnail cache analysis.
