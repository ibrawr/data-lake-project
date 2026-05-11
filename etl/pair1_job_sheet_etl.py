import os
import json
import pandas as pd

config = json.load(open("config.json"))
BASE = config["LOCAL_DATA_PATH"]

job_sheet_dir = os.path.join(BASE, "Vendors")

all_rows = []

for vendor in os.listdir(job_sheet_dir):
    vpath = os.path.join(job_sheet_dir, vendor, "job_sheet.csv")
    if os.path.exists(vpath):
        df = pd.read_csv(vpath)
        df["vendor"] = vendor
        all_rows.append(df)

full_df = pd.concat(all_rows, ignore_index=True)

# Cleaning
full_df["date"] = pd.to_datetime(full_df["date"], errors="coerce")
full_df["total_amount"] = full_df["total_amount"].astype(float)

# Trend analytics
monthly_trend = full_df.groupby(full_df["date"].dt.to_period("M"))["total_amount"].sum().reset_index()
monthly_trend["date"] = monthly_trend["date"].astype(str)

# Save to curated zone
os.makedirs("curated_data", exist_ok=True)
monthly_trend.to_parquet("curated_data/pair1_job_sheets.parquet", index=False)

print("Pair 1 job sheet ETL complete.")
