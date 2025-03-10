import pandas as pd

# Load dataset
file_path = "stuttering_features_with_labels.csv"
df = pd.read_csv(file_path)

# Define the 5 main stuttering classes
MAIN_CLASSES = ["Prolongation", "Block", "WordRep", "SoundRep", "Interjection"]

# Convert multi-labels into separate categories
df["label"] = df["label"].astype(str)  # Ensure labels are strings
df["label"] = df["label"].apply(lambda x: x.replace('"', '').split(","))  # Remove quotes and split labels

# Create binary columns for each class
for cls in MAIN_CLASSES:
    df[cls] = df["label"].apply(lambda x: 1 if cls in x else 0)

# Drop the original "label" column since it's now one-hot encoded
df.drop(columns=["label"], inplace=True)

# Save the modified dataset
df.to_csv("stuttering_features_onehot.csv", index=False)

# Display the first few rows
print(df.head())