#!/usr/bin/env python3
"""
Improved morse decoder with better timing detection
"""

import wave
import numpy as np
from scipy import signal

MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    '----': '4',  # Alternative encoding
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.-...': '{', '-..-.': '}',
}

def read_wav(filename):
    with wave.open(filename, 'r') as wav_file:
        sample_rate = wav_file.getframerate()
        audio_data = wav_file.readframes(wav_file.getnframes())
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    return audio_array, sample_rate

def detect_envelope(audio, sample_rate):
    # Normalize
    audio = audio.astype(np.float32) / np.max(np.abs(audio))

    # Simple envelope detection using absolute value and smoothing
    envelope = np.abs(audio)

    # Smooth
    window = int(sample_rate * 0.005)  # 5ms
    kernel = np.ones(window) / window
    envelope_smooth = np.convolve(envelope, kernel, mode='same')

    # Adaptive threshold
    threshold = np.mean(envelope_smooth) + 0.5 * np.std(envelope_smooth)
    binary = (envelope_smooth > threshold).astype(int)

    return binary

def analyze_timing(binary, sample_rate):
    """Analyze timing to determine unit duration."""
    diff = np.diff(np.concatenate([[0], binary, [0]]))
    on_idx = np.where(diff == 1)[0]
    off_idx = np.where(diff == -1)[0]

    if len(on_idx) == 0:
        return None

    # Signal durations
    signals = (off_idx - on_idx) / sample_rate
    # Gap durations
    gaps = (on_idx[1:] - off_idx[:-1]) / sample_rate if len(on_idx) > 1 else []

    # Find unit (shortest consistent duration)
    all_dur = np.concatenate([signals, gaps])
    all_dur = all_dur[all_dur > 0.01]  # Remove very short noise

    if len(all_dur) == 0:
        return None

    # Unit is typically the shortest duration cluster
    unit = np.min(all_dur)

    return unit, signals, gaps

def decode_with_unit(signals, gaps, unit):
    """Decode using detected unit duration."""
    morse_chars = []
    current = []

    for i, sig_dur in enumerate(signals):
        # Dot or dash?
        if sig_dur / unit < 2:
            current.append('.')
        else:
            current.append('-')

        # Check gap
        if i < len(gaps):
            gap_ratio = gaps[i] / unit
            if gap_ratio > 5:  # Word space
                if current:
                    morse_chars.append(''.join(current))
                current = []
                morse_chars.append(' ')
            elif gap_ratio > 2.5:  # Letter space
                if current:
                    morse_chars.append(''.join(current))
                current = []

    if current:
        morse_chars.append(''.join(current))

    return morse_chars

def morse_to_text(morse_list):
    result = []
    for m in morse_list:
        if m == ' ':
            result.append(' ')
        elif m in MORSE_CODE:
            result.append(MORSE_CODE[m])
        else:
            result.append(f'[{m}]')
    return ''.join(result)

def main():
    print("Reading for400_morse.wav...")
    audio, sr = read_wav("for400_morse.wav")
    print(f"Sample rate: {sr} Hz, Duration: {len(audio)/sr:.2f}s")

    print("Detecting envelope...")
    binary = detect_envelope(audio, sr)

    print("Analyzing timing...")
    result = analyze_timing(binary, sr)
    if result is None:
        print("ERROR: Could not detect morse signal")
        return

    unit, signals, gaps = result
    print(f"Unit duration: {unit*1000:.1f}ms")
    print(f"Signals detected: {len(signals)}")

    print("\nDecoding...")
    morse_chars = decode_with_unit(signals, gaps, unit)

    morse_str = ' | '.join(morse_chars)
    print(f"\nMorse: {morse_str}")

    text = morse_to_text(morse_chars)
    print(f"\nDecoded: {text}")

    with open("morse_decoded_v2.txt", "w") as f:
        f.write(f"Morse: {morse_str}\n\nText: {text}\n")

    print("\n✓ Saved to morse_decoded_v2.txt")

if __name__ == "__main__":
    main()
