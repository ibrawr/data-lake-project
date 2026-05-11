import os
import json
import pandas as pd

# -------------------------------
# Load local dataset path
# -------------------------------
config = json.load(open("config.json"))
BASE = config["LOCAL_DATA_PATH"]

logs_dir = os.path.join(BASE, "Logs")

# -------------------------------
# Load and merge all log files
# -------------------------------
all_logs = []

for file in os.listdir(logs_dir):
    if file.endswith(".csv"):
        fpath = os.path.join(logs_dir, file)
        df = pd.read_csv(fpath)
        df["source_file"] = file
        all_logs.append(df)

full_logs = pd.concat(all_logs, ignore_index=True)

# -------------------------------
# Cleaning
# -------------------------------
full_logs["timestamp"] = pd.to_datetime(full_logs["timestamp"], errors="coerce")

# -------------------------------
# Analytics 1: Daily activity summary
# -------------------------------
full_logs["date"] = full_logs["timestamp"].dt.date

daily_activity = full_logs.groupby(["date", "event_type"]).size().unstack(fill_value=0)
daily_activity.reset_index(inplace=True)

# -------------------------------
# Analytics 2: User activity summary
# -------------------------------
user_summary = full_logs.groupby(["user", "event_type"]).size().unstack(fill_value=0)
user_summary["total_events"] = user_summary.sum(axis=1)
user_summary.reset_index(inplace=True)

# -------------------------------
# Analytics 3: System usage summary
# -------------------------------
system_summary = full_logs.groupby(["system", "event_type"]).size().unstack(fill_value=0)
system_summary["total_events"] = system_summary.sum(axis=1)
system_summary.reset_index(inplace=True)

# -------------------------------
# Save output to curated zone
# -------------------------------
os.makedirs("curated_data/logs", exist_ok=True)

full_logs.to_parquet("curated_data/logs/logs_full.parquet", index=False)
daily_activity.to_parquet("curated_data/logs/logs_daily_activity.parquet", index=False)
user_summary.to_parquet("curated_data/logs/logs_user_summary.parquet", index=False)
system_summary.to_parquet("curated_data/logs/logs_system_summary.parquet", index=False)

print("Logs ETL pipeline completed successfully.")