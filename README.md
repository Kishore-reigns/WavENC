# WavENC
In the era of rapid digital communication, ensuring the confidentiality and integrity of audio data has become a critical challenge. This project, WavENC, presents a robust framework for audio encryption and decryption using the Advanced Encryption Standard (AES) algorithm. The system converts raw audio samples from .wav files into frame-level binary data, which is then encrypted using a password-derived AES key. The encryption process produces both a securely stored ciphertext file and an optional playable encrypted audio stream to enable experimental visualization. Upon decryption, the original waveform is perfectly reconstructed, validating the system’s fidelity and reversibility.

Additionally, WavENC integrates waveform and frequency-domain visualization to analyze the effects of encryption on audio characteristics. This framework demonstrates the practical application of modern symmetric cryptography in securing multimedia content, ensuring resistance against unauthorized access and eavesdropping.


# Dependencies to install

* pycryptodome — provides AES encryption and key derivation.

* numpy — handles frame-level numeric operations on PCM data.

* matplotlib — visualizes waveforms and frequency spectra.

You can downlaod it from requirements.txt with the help of the command below 

```bash
pip install -r requirements.txt
```

If you face any error while installing or using the crypto package, then uninstall all other packages related to cryptography and try install pycryptodome again.


# Sample audio

The sample audio is given in the path directory sample_audio

[Listen to the sample audio](sample_audio/wannbeWav.wav)

# How to use

To encrypt use the command below

```bash
python audioEnc.py <audio_path> <password>
```

To decrypt use the command

```bash
python audioDec.py <audio_path> <same password which is used to encrypt>
```

### Sample outputs are given in dir sample_encryption_output and sample_decryption_output



