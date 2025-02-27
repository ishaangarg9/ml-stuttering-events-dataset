import os
import glob

def clean_filenames(directory):
    # Find all .wav files in the directory
    for filepath in glob.glob(os.path.join(directory, "*.wav")):
        # Extract directory and filename
        dir_name, filename = os.path.split(filepath)
        
        # Remove spaces from filename
        new_filename = filename.replace(" ", "")
        new_filepath = os.path.join(dir_name, new_filename)
        
        # Rename the file if necessary
        if new_filepath != filepath:
            os.rename(filepath, new_filepath)
            print(f"Renamed: {filepath} -> {new_filepath}")

if __name__ == "__main__":
    directory = "wavs/StutterTalk/"
    clean_filenames(directory)