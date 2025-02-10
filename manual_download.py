import os
import csv
import requests
import subprocess

# Define directories
DOWNLOAD_DIR = "wavs/FluencyBank/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Your session cookie (Paste it from your browser)
COOKIES = {
    "sessionid": "s%3AlbTk33cNTWbhzq-RnJvkxV4OsJETnkpQ.yTabHvlYEfNu%2FvD8g6YcJd2%2Bb%2Fz0Gr72Yym3027%2FDnk"  # Replace this
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Read CSV file
csv_file = "fluencybank_episodes.csv"
with open(csv_file, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 3:
            continue  # Skip invalid rows
        
        episode_name = row[1].strip()
        url = row[2].strip()
        mp4_path = os.path.join(DOWNLOAD_DIR, f"{episode_name}.mp4")
        wav_path = os.path.join(DOWNLOAD_DIR, f"{episode_name}.wav")

        # Download MP4 file using session cookies
        print(f"Downloading: {url}")
        response = requests.get(url, cookies=COOKIES, headers=HEADERS, stream=True)

        if response.status_code != 200:
            print(f"Failed to download {episode_name}: HTTP {response.status_code}")
            continue

        with open(mp4_path, "wb") as video_file:
            video_file.write(response.content)

        # Check if the file is valid
        if os.path.getsize(mp4_path) < 1000:  # Likely an error page
            print(f"Error: {mp4_path} is too small ({os.path.getsize(mp4_path)} bytes). Deleting.")
            os.remove(mp4_path)
            continue

        # Convert MP4 to WAV
        print(f"Converting {mp4_path} to {wav_path}")
        try:
            subprocess.run(["ffmpeg", "-i", mp4_path, "-ac", "1", "-ar", "16000", wav_path], check=True)
            os.remove(mp4_path)  # Delete MP4 after conversion
            print(f"Saved WAV: {wav_path}")
        except subprocess.CalledProcessError:
            print(f"Error converting {episode_name}")

print("Download and conversion completed.")