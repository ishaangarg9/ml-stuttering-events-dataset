import os
import pathlib
import subprocess
import argparse

def convert_mp4_to_wav(directory):
    directory = pathlib.Path(directory)
    os.makedirs(directory, exist_ok=True)

    for mp4_file in directory.glob("*.mp4"):
        wav_file = directory / f"{mp4_file.stem}.wav"
        
        if wav_file.exists():
            print(f"Skipping {wav_file}, already exists.")
            continue
        
        print(f"Converting {mp4_file} to {wav_file}...")
        ffmpeg_cmd = f'ffmpeg -i "{mp4_file}" -ac 1 -ar 16000 "{wav_file}"'
        subprocess.run(ffmpeg_cmd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert MP4 files to WAV without deleting the MP4 files.')
    parser.add_argument('--directory', type=str, required=True, help='Directory containing MP4 files and where WAV files will be saved')
    
    args = parser.parse_args()
    convert_mp4_to_wav(args.directory)
