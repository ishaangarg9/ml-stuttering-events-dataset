import os
import pathlib
import numpy as np
import pandas as pd
from scipy.io import wavfile
import argparse
from pathlib import Path
parser = argparse.ArgumentParser(description='Extract clips from SEP-28k or FluencyBank.')
parser.add_argument('--labels', type=str, required=True, help='Path to labels CSV file (e.g., SEP-28k_labels.csv)')
parser.add_argument('--wavs', type=str, default="wavs", help='Path where audio files are saved')
parser.add_argument('--clips', type=str, default="clips", help='Path where clips should be extracted')
parser.add_argument("--progress", action="store_true", help="Show progress")

args = parser.parse_args()
label_file = args.labels
data_dir = args.wavs
output_dir = args.clips

# Load labels
data = pd.read_csv(label_file, dtype={"EpId": str})

shows = data.Show
episodes = data.EpId
clip_idxs = data.ClipId
starts = data.Start
stops = data.Stop

n_items = len(shows)
loaded_wav = ""
cur_iter = range(n_items)

if args.progress:
    from tqdm import tqdm
    cur_iter = tqdm(cur_iter)

for i in cur_iter:
    clip_idx = clip_idxs[i]
    show_abrev = shows[i]
    episode = episodes[i].strip()

    wav_path = pathlib.Path(data_dir) / shows[i].strip() / f"{episode.strip()}.wav"
    clip_dir = pathlib.Path(output_dir) / show_abrev.strip() / episode.strip()
    clip_path = clip_dir / f"{shows[i].strip()}_{episode.strip()}_{clip_idx}.wav"

    print(f"Checking file: {wav_path}")
    print(f"Exists: {wav_path.exists()}")
    if not os.path.exists(wav_path):
        print(f"Missing WAV file: {wav_path}")
        continue

    os.makedirs(clip_dir, exist_ok=True)

    # Load audio only if it's a new file
    if wav_path != loaded_wav:
        sample_rate, audio = wavfile.read(wav_path)
        if sample_rate != 16000:
            print(f"Skipping {wav_path}: Incorrect sample rate ({sample_rate} Hz)")
            continue
        loaded_wav = wav_path

    # Validate timestamps
    if pd.isna(starts[i]) or pd.isna(stops[i]):
        print(f"Skipping {clip_path} due to missing timestamps")
        continue

    if starts[i] < 0 or stops[i] > len(audio) or starts[i] >= stops[i]:
        print(f"Skipping {clip_path}: Invalid time range ({starts[i]}, {stops[i]})")
        continue

    # Save clip
    clip = audio[int(starts[i]):int(stops[i])]
    wavfile.write(clip_path, sample_rate, clip)