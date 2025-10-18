"""
audio_decrypt.py

Decrypt AES-encrypted WAV data (from .enc file) and restore the original WAV.
Plots decrypted waveform and frequency spectrum.

Usage:
    python audio_decrypt.py input_encrypted.enc password
"""

import os
import sys
import wave
import struct
import hashlib
from Crypto.Cipher import AES
import numpy as np
import matplotlib.pyplot as plt


# --------------------------- #
# Utility
# --------------------------- #
def derive_aes_key(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).digest()

def pkcs7_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]

def aes_decrypt_bytes(key: bytes, iv_and_ciphertext: bytes) -> bytes:
    iv = iv_and_ciphertext[:16]
    ciphertext = iv_and_ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ciphertext)
    return pkcs7_unpad(padded)

def write_wav_file(path: str, framerate: int, sampwidth: int, n_channels: int, frames_bytes: bytes):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(frames_bytes)

def read_wav_file(path: str):
    with wave.open(path, 'rb') as wf:
        return wf.getframerate(), wf.getsampwidth(), wf.getnchannels(), wf.readframes(wf.getnframes())


# --------------------------- #
# WAV Decryption Workflow
# --------------------------- #
def decrypt_wav_frames_from_file(enc_path: str, out_wav_path: str, password: str):
    with open(enc_path, 'rb') as f:
        data = f.read()
    magic = data[:8]
    if magic != b'AUDENC01':
        raise ValueError("Invalid encrypted file format.")
    sampwidth = data[8]
    nchannels = data[9]
    framerate = struct.unpack('<I', data[10:14])[0]
    iv_and_cipher = data[14:]
    key = derive_aes_key(password)
    frames = aes_decrypt_bytes(key, iv_and_cipher)
    write_wav_file(out_wav_path, framerate, sampwidth, nchannels, frames)
    print(f"Decrypted WAV saved to: {out_wav_path}")
    return out_wav_path


# --------------------------- #
# Plotting
# --------------------------- #
def plot_waveform_and_spectrum(enc_path, dec_wav, save_prefix):
    with open(enc_path, 'rb') as f:
        enc_data = f.read()[14:]
    enc_vis = np.frombuffer(enc_data, dtype=np.int16)
    fr, sw, ch, frames = read_wav_file(dec_wav)
    arr = np.frombuffer(frames, dtype=np.int16)

    # Waveform comparison
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title("Encrypted Data - Waveform-like")
    plt.plot(enc_vis[:5000])
    plt.subplot(2, 1, 2)
    plt.title("Decrypted Audio - Waveform")
    plt.plot(arr[:5000])
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_waveforms.png", dpi=200)
    plt.close()

    # FFT
    def compute_fft(a, sr, n=4096):
        Y = np.fft.rfft(a[:n])
        f = np.fft.rfftfreq(n, 1.0/sr)
        return f, np.abs(Y)

    f1, m1 = compute_fft(enc_vis, fr)
    f2, m2 = compute_fft(arr, fr)
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title("Encrypted Data - Spectrum (visualized)")
    plt.semilogy(f1, m1)
    plt.subplot(2, 1, 2)
    plt.title("Decrypted Audio - Spectrum")
    plt.semilogy(f2, m2)
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_spectra.png", dpi=200)
    plt.close()
    print(f"Saved plots: {save_prefix}_waveforms.png, {save_prefix}_spectra.png")


# --------------------------- #
# Main
# --------------------------- #
def main(enc_file: str, password: str):
    base = os.path.splitext(os.path.basename(enc_file))[0]
    out_wav = base + "_decrypted.wav"
    decrypt_wav_frames_from_file(enc_file, out_wav, password)
    plot_waveform_and_spectrum(enc_file, out_wav, base)
    print("Decryption and plotting complete.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audio_decrypt.py input_encrypted.enc password")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
