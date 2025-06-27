# Contoso Call Center Synthetic Transcript and Audio Generator

A Python-based application designed to generate synthetic call center conversations and corresponding audio files for Contoso Medical.

## Features

- Generate synthetic call transcripts for three medical scenarios:
  1. Healthcare provider inquiring about a past patient encounter
  2. Patient calling about a recent visit to a hospital, clinic, or emergency room
  3. Caregiver calling with a medical question about a patient under Contoso Medical's care

- Support mixed sentiment in conversations (positive, neutral, negative)
- Generate realistic but fictitious PHI and PII data
- Generate .wav audio files from transcripts using text-to-speech synthesis
- User-friendly interface for configuring call parameters

## Audio Specifications

- File Format: WAV (Microsoft PCM)
- Bit Depth: 16-bit
- Sampling Rate: 8 kHz, 16 kHz, 32 kHz, or 48 kHz
- Channels: Mono (recommended) or Stereo
- Bitrate: 256 kbps (mono), 512 kbps (stereo)
- Codec: PCM

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

## Disclaimer

All generated data is synthetic and fictitious. This application is for simulation purposes only and does not contain real PHI or PII data.
