import os
import pathlib
import subprocess
import pandas as pd
import requests
import argparse

parser = argparse.ArgumentParser(description='Download raw audio files for SEP-28k or FluencyBank and convert to 16k hz mono wavs.')
parser.add_argument('--episodes', type=str, required=True, help='Path to the labels csv file (e.g., SEP-28k_episodes.csv)')
parser.add_argument('--wavs', type=str, default="wavs", help='Path where audio files are saved')

args = parser.parse_args()
episode_uri = args.episodes
wav_dir = args.wavs

# Load episode data
table = pd.read_csv(episode_uri, delimiter=",", dtype=str).values
urls = table[:, 2]
n_items = len(urls)

audio_types = [".mp3", ".m4a", ".mp4"]

def download_audio(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download {url}")

for i in range(n_items):
    show_abrev = table[i, -2]
    ep_idx = table[i, -1]
    episode_url = table[i, 2]

    ext = next((e for e in audio_types if episode_url.endswith(e)), "")
    if not ext:
        print(f"Skipping {episode_url}, unknown format.")
        continue

    episode_dir = pathlib.Path(f"{wav_dir}/{show_abrev}/")
    os.makedirs(episode_dir, exist_ok=True)

    audio_path_orig = pathlib.Path(f"{episode_dir}/{ep_idx}{ext}")
    wav_path = pathlib.Path(f"{episode_dir}/{ep_idx}.wav")

    if os.path.exists(wav_path):
        continue

    print(f"Processing {show_abrev} {ep_idx}")

    if not os.path.exists(audio_path_orig):
        download_audio(episode_url, audio_path_orig)

    if os.path.exists(audio_path_orig):
        ffmpeg_cmd = f'ffmpeg -i "{audio_path_orig}" -ac 1 -ar 16000 "{wav_path}"'
        subprocess.run(ffmpeg_cmd, shell=True)

        os.remove(audio_path_orig)  # Remove only if the conversion was successful