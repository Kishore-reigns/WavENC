"""
audio_encrypt.py

Encrypt a WAV file using AES-256 (CBC), save encrypted data, and
optionally generate a playable encrypted WAV + waveform and spectrum plots.

Usage:
    python audio_encrypt.py input.wav password
"""

import os
import sys
import wave
import struct
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import numpy as np
import matplotlib.pyplot as plt


# --------------------------- #
# Utility: Key + Padding
# --------------------------- #
def derive_aes_key(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).digest()

def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


# --------------------------- #
# WAV read/write helpers
# --------------------------- #
def read_wav_file(path: str):
    with wave.open(path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)
    return framerate, sampwidth, n_channels, frames

def write_wav_file(path: str, framerate: int, sampwidth: int, n_channels: int, frames_bytes: bytes):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(frames_bytes)


# --------------------------- #
# AES Encryption
# --------------------------- #
def aes_encrypt_bytes(key: bytes, plaintext: bytes) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pkcs7_pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return iv + ciphertext


# --------------------------- #
# WAV Encryption Workflow
# --------------------------- #
def encrypt_wav_frames_to_file(wav_path: str, out_enc_path: str, password: str):
    framerate, sampwidth, nchannels, frames = read_wav_file(wav_path)
    key = derive_aes_key(password)
    iv_cipher = aes_encrypt_bytes(key, frames)

    enc_wav_path = os.path.splitext(out_enc_path)[0] + "_playable.wav"

    # Create playable encrypted WAV
    if sampwidth == 2:
        enc_samples = np.frombuffer(iv_cipher[:(len(iv_cipher)//2)*2], dtype=np.int16)
        enc_bytes = enc_samples.tobytes()
        enc_sampwidth = 2
    else:
        enc_bytes = iv_cipher
        enc_sampwidth = 1

    write_wav_file(enc_wav_path, framerate, enc_sampwidth, nchannels, enc_bytes)
    print(f"Playable encrypted WAV saved to: {enc_wav_path}")

    with open(out_enc_path, 'wb') as f:
        magic = b'AUDENC01'
        header = magic + struct.pack('<B', sampwidth) + struct.pack('<B', nchannels) + struct.pack('<I', framerate)
        f.write(header + iv_cipher)

    print(f"Encrypted data saved to: {out_enc_path}")
    return out_enc_path, enc_wav_path


# --------------------------- #
# Plotting
# --------------------------- #
def plot_waveform_and_spectrum(original_wav, enc_path, save_prefix):
    fr1, sw1, ch1, frames1 = read_wav_file(original_wav)
    arr1 = np.frombuffer(frames1, dtype=np.int16 if sw1 == 2 else np.uint8)
    with open(enc_path, 'rb') as f:
        enc_data = f.read()[14:]
    enc_vis = np.frombuffer(enc_data, dtype=np.int16)

    # Waveform plot
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title("Original Audio - Waveform")
    plt.plot(arr1[:5000])
    plt.subplot(2, 1, 2)
    plt.title("Encrypted Bytes (visualized) - Waveform-like")
    plt.plot(enc_vis[:5000])
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_waveforms.png", dpi=200)
    plt.close()

    # FFT Spectrum
    def compute_fft(arr, n=4096):
        Y = np.fft.rfft(arr[:n])
        f = np.fft.rfftfreq(n, 1.0 / fr1)
        return f, np.abs(Y)

    f1, m1 = compute_fft(arr1)
    f2, m2 = compute_fft(enc_vis)
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title("Original Audio - Spectrum")
    plt.semilogy(f1, m1)
    plt.subplot(2, 1, 2)
    plt.title("Encrypted Bytes - Spectrum (visualized)")
    plt.semilogy(f2, m2)
    plt.tight_layout()
    plt.savefig(f"{save_prefix}_spectra.png", dpi=200)
    plt.close()
    print(f"Saved plots: {save_prefix}_waveforms.png, {save_prefix}_spectra.png")


# --------------------------- #
# Main
# --------------------------- #
def main(wav_path: str, password: str):
    base = os.path.splitext(os.path.basename(wav_path))[0]
    enc_path = base + "_encrypted.enc"
    enc_path, playable_enc = encrypt_wav_frames_to_file(wav_path, enc_path, password)
    plot_waveform_and_spectrum(wav_path, enc_path, base)
    print(f"Done.\nEncrypted: {enc_path}\nPlayable: {playable_enc}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python audio_encrypt.py input.wav password")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
