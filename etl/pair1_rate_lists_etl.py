import os
import json
import pandas as pd

# Load config
config = json.load(open("config.json"))
BASE = config["LOCAL_DATA_PATH"]

rate_dir = os.path.join(BASE, "Rate_Lists")

all_rows = []

for file in os.listdir(rate_dir):
    if file.endswith(".csv"):
        fpath = os.path.join(rate_dir, file)
        df = pd.read_csv(fpath)

        # Add file source
        df["source_file"] = file
        
        all_rows.append(df)

# Combine
full_df = pd.concat(all_rows, ignore_index=True)

# Cleaning
full_df.columns = [c.strip().lower() for c in full_df.columns]

num_cols = ["hourly_rate", "daily_rate", "monthly_rate", "overtime_rate"]

for col in num_cols:
    full_df[col] = pd.to_numeric(full_df[col], errors="coerce")

# Normalize Yes/No fields
bool_cols = ["driver_included", "fuel_included"]

for col in bool_cols:
    full_df[col] = full_df[col].str.strip().str.lower().map({
        "yes": True,
        "no": False
    })

# --- Analytics ---

# A. Average rates per vehicle type
avg_rates = full_df.groupby("vehicle_type")[num_cols].mean().reset_index()

# Save curated
os.makedirs("curated_data", exist_ok=True)
full_df.to_parquet("curated_data/rate_lists.parquet", index=False)
avg_rates.to_parquet("curated_data/rate_lists_avg_rates.parquet", index=False)

print("Rate Lists ETL complete.")