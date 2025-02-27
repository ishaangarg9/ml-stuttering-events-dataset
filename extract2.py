import os
import pathlib
import numpy as np
import pandas as pd
from scipy.io import wavfile
import argparse
from tqdm import tqdm

# Argument parsing
parser = argparse.ArgumentParser(description='Extract 3-second WAV clips from dataset.')
parser.add_argument('--labels', type=str, required=True, help='Path to labels CSV file')
parser.add_argument('--wavs', type=str, default="wavs", help='Path to input WAV files')
parser.add_argument('--clips', type=str, default="clips", help='Path to store extracted clips')
parser.add_argument('--progress', action='store_true', help='Show extraction progress')
args = parser.parse_args()

# Load labels
data = pd.read_csv(args.labels, dtype={"EpId": str})

# Iterate over dataset
for _, row in tqdm(data.iterrows(), total=len(data), disable=not args.progress):
    show, ep_id, clip_id, start, stop = row['Show'], row['EpId'].strip(), row['ClipId'], row['Start'], row['Stop']
    
    wav_path = pathlib.Path(args.wavs) / show / f"{ep_id}.wav"
    clip_dir = pathlib.Path(args.clips) / show / ep_id
    clip_path = clip_dir / f"{show}_{ep_id}_{clip_id}.wav"
    print(f"Expected Path: '{wav_path}'")
    print(f"Absolute Path: '{os.path.abspath(wav_path)}'")
    print(f"File Exists? {os.path.exists(os.path.abspath(wav_path))}")
    if not wav_path.exists():
        print(f"Missing WAV file: {wav_path}")
        continue
    
    os.makedirs(clip_dir, exist_ok=True)
    
    # Load audio
    sample_rate, audio = wavfile.read(wav_path)
    if sample_rate != 16000:
        print(f"Skipping {wav_path}: Incorrect sample rate ({sample_rate} Hz)")
        continue
    
    # Validate timestamps
    if pd.isna(start) or pd.isna(stop) or start < 0 or stop > len(audio) or start >= stop:
        print(f"Skipping {clip_path}: Invalid time range ({start}, {stop})")
        continue
    
    # Extract and save clip
    clip = audio[int(start):int(stop)]
    wavfile.write(clip_path, sample_rate, clip)
    print(f"Saved: {clip_path}")
