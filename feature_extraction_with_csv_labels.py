import os
import librosa
import numpy as np
import pandas as pd
from tqdm import tqdm

# Set Paths
DATASET_PATH = "clips"  # Path where audio clips are stored
CSV_PATH = "SEP-28k_labels.csv"  # Path to the CSV file

# Load CSV file
df_csv = pd.read_csv(CSV_PATH)

# Select relevant columns for labels
labels_cols = ["Prolongation", "Block", "SoundRep", "WordRep", "Interjection"]
df_csv["label"] = df_csv[labels_cols].apply(lambda row: ",".join(row.index[row > 0]), axis=1)

# Function to extract audio features
import soundfile as sf

def extract_features(file_path):
    try:
        # Use soundfile instead of librosa for better AIFF-C support
        y, sr = sf.read(file_path, always_2d=True)
        y = y[:, 0]  # Convert stereo to mono if necessary
        
        # Extract Features
        mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T, axis=0)
        chroma = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr).T, axis=0)
        zcr = np.mean(librosa.feature.zero_crossing_rate(y).T, axis=0)
        rmse = np.mean(librosa.feature.rms(y=y).T, axis=0)

        return np.hstack([mfccs, chroma, spectral_contrast, zcr, rmse])
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Store extracted features
data = []
labels = []  # Stuttering class labels
file_names = []  # Track file names

# Traverse dataset and match files to CSV labels
for root, dirs, files in os.walk(DATASET_PATH):
    for file in tqdm(files):
        if file.endswith(".wav"):
            file_path = os.path.join(root, file)

            # Extract metadata from filename: Show, EpId, ClipId
            parts = file.replace(".wav", "").split("_")  # Assuming format: Show_EpId_ClipId.wav
            if len(parts) < 3:
                continue
            
            show, ep_id, clip_id = parts[0], int(parts[1]), int(parts[2])
            
            # Find matching row in CSV
            match = df_csv[(df_csv["Show"] == show) & (df_csv["EpId"] == ep_id) & (df_csv["ClipId"] == clip_id)]
            if match.empty:
                continue
            
            # Get multi-label stuttering class
            label = match["label"].values[0]

            # Extract features
            features = extract_features(file_path)
            if features is not None:
                data.append(features)
                labels.append(label)
                file_names.append(file)

# Convert to DataFrame
df_features = pd.DataFrame(data)
df_features["label"] = labels
df_features["filename"] = file_names

# Save to CSV
df_features.to_csv("stuttering_features_with_labels.csv", index=False)
print("✅ Feature extraction complete! Saved to 'stuttering_features_with_labels.csv'")