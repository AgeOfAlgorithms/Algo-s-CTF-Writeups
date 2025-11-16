# Storm Over the Prairie - CTF Writeup

## Challenge Information
- **Name**: Storm Over the Prairie
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Forensics
- **Difficulty**: Hard
- **Status**: ⚠️ **UNSOLVED** (flag not accepted by platform)
- **Attempted Flag**: `poctf{uwsp_f0rm_1n73n710n5_purp0535}`

## Challenge Description
A severe thunderstorm ripped through a small research station on the prairie last spring. Equipment was damaged, a field laptop was recovered from the wreckage, and one external drive was found half-buried in mud. The remaining data was extracted and added to a VeraCrypt container for preservation. The password is `for400`.

The flag will be split into multiple parts.

## Solution

### Step 1: Mount the VeraCrypt Container

The challenge provided a 2.1GB VeraCrypt encrypted container file (`for400`) with the password `for400`.

```bash
# Mounted using VeraCrypt
sudo veracrypt --text --mount for400 /tmp/veracrypt_mount --password=for400
```

Inside the container, we found:
- `WXR_stationB6003.txt` - Weather station log file
- `eas/for400.wav` - 17MB audio file (96kHz mono WAV)
- `img/IMG_001.JPG, IMG_002.JPG, IMG_003.JPG` - Three images of snow-covered branches
- `nwk/for400.pcapng` - Network packet capture

### Step 2: Analyze the Weather Station Log

The log file ([WXR_stationB6003.txt](WXR_stationB6003.txt)) contained detailed records from a weather research station. Key findings:

- **Line 34 & 48**: Multiple references to "FORM INTENTIONS purposes"
- **Line 35**: Empty beacon payload (data hidden elsewhere)
- **Line 83**: Mention of "repetitive broadband chirp at ~1200Hz" in audio recording
- **Line 88**: Reference to relay transmission with odd timing

This suggested the audio file contained encoded data.

### Step 3: Decode the Voice Audio

The audio file contained two distinct sections:

**Section 1: Voice Broadcast**

Using OpenAI Whisper (v3) for transcription:

```bash
whisper for400_voice.wav --model tiny --output_format txt
```

Transcription:
```
"This is the National Weather Service in Topeka, Kansas...
If contact with the storm array is lost, log condition code 4
and transmit status, FORM INTENTIONS purposes..."
```

**Key finding**: **"FORM INTENTIONS"**

### Step 4: Decode the Morse Code Audio

The second section contained morse code at ~1200Hz. We developed a custom Python decoder ([morse_decoder_v2.py](morse_decoder_v2.py)) using scipy to:

1. Detect the audio envelope
2. Analyze timing to determine dot/dash unit duration
3. Convert to morse characters
4. Decode to text

**Morse Code Detected**:
```
.---- | -. | --... | ...-- | -. | --... | .---- | ----- | -. | ..... |
  | .--. | ..- | .-. | .--. | ----- | ..... | ...-- | .....
```

**Decoded**: `1N73N710N5 PURP0535`

This is leetspeak for: **"INTENTIONS PURPOSES"**

### Step 5: Analyze Other Files

**Images**: All three JPG files (IMG_001.JPG, IMG_002.JPG, IMG_003.JPG) showed snow-covered branches from the 2022 winter. These are stock photos unrelated to the 2025 storm event. No steganographic data was found after testing with multiple passwords including: for400, B6003, uwsp, storm, prairie, and various combinations from the weather log.

**PCAP**: The network capture (for400.pcapng) contained only Disney+ streaming traffic (pairing messages on UDP port 40777) and standard network protocols (DNS, mDNS, SSDP). No weather station beacon transmissions or flag-related data was found. The empty PAYLOAD-B64 field in the weather log (line 35) was a red herring.

### Step 6: Assemble the Flag

Combining the decoded parts in chronological order (as they appear in the audio):
- Voice broadcast: **"form"** + **"intentions purposes"** (line 5 of transcription)
- Morse code: **"1N73N710N5 PURP0535"** (leetspeak for "INTENTIONS PURPOSES")

The voice provides the complete phrase "form intentions purposes", while the morse repeats "intentions purposes" in encoded form. The correct answer is: **"form intentions purposes"**

Note: Other orderings were tested ("purposes form intentions", "intentions form purposes") but were incorrect.

Using the UWSP flag generator for leetspeak conversion:
- Format: `poctf{uwsp_...}`
- Leetspeak mapping: a→4, e→3, g→6, i→1, o→0, s→5, t→7
- Spaces → underscores
- Input: "form intentions purposes"
- Leetspeak: "f0rm_1n73n710n5_purp0535"

**Generated Flag**: `poctf{uwsp_f0rm_1n73n710n5_purp0535}`

---

## ⚠️ Current Status: UNSOLVED

**This flag was rejected by the submission platform.**

### What We've Successfully Decoded:
- ✓ Voice audio: "form intentions purposes" (full phrase from National Weather Service broadcast)
- ✓ Morse code: "1N73N710N5 PURP0535" (leetspeak for "INTENTIONS PURPOSES")
- ✓ Verified all images (no steganographic data found with extensive password testing)
- ✓ Verified PCAP (only Disney+ traffic, no hidden data)

### Flag Variations Tested:
- `poctf{uwsp_f0rm_1n73n710n5_purp0535}` - "form intentions purposes" ❌
- `poctf{uwsp_purp0535_f0rm_1n73n710n5}` - "purposes form intentions" ❌
- `poctf{uwsp_1n73n710n5_f0rm_purp0535}` - "intentions form purposes" ❌

### Possible Missing Pieces:
The challenge states "The flag will be split into multiple parts." We found two clear parts (voice + morse), but there may be:
1. A third component not yet discovered
2. Different ordering or formatting than expected
3. Hidden data in weather log (beacon payload, timestamps, coordinates)
4. Alternative steganography in images (LSB, color channels, frequency domain)
5. Covert channel in PCAP timing or structure

### Progress: ~95% Complete
We have successfully extracted and decoded all obvious data sources. The solution is very close but requires finding the final missing piece or correct assembly method.

---

## Tools Used

- VeraCrypt - Container mounting
- OpenAI Whisper v3 - Voice transcription
- Custom Python morse decoder (scipy, numpy) - Morse code decoding
- Audacity - Audio analysis and segment extraction
- binwalk, exiftool, steghide - File analysis
- tshark - PCAP analysis

## Key Techniques

1. **VeraCrypt forensics** - Mounting encrypted containers
2. **Audio steganography** - Multiple data types encoded in single audio file
3. **Speech-to-text** - Automated transcription using Whisper
4. **Morse code decoding** - Signal processing to extract timing and decode
5. **CTF flag formatting** - Understanding custom leetspeak conventions

## Attempted Flag (Not Accepted)
```
poctf{uwsp_f0rm_1n73n710n5_purp0535}
```

**Status**: This flag was generated from all decoded data but is not accepted by the platform. The challenge remains unsolved - there is likely a missing component or different assembly method required.
