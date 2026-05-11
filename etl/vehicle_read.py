import os
import json
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image

# ============================================================
# CONFIG
# ============================================================

# Raw input data
REG_BASE = "raw/Vehicle_Registration"
CHECKLIST_BASE = "raw/Vehicle_Checklist"

# Processed outputs
PROCESSED_BASE = "processed"

# Metadata
METADATA_PATH = os.path.join(PROCESSED_BASE, "metadata", "processed_files.json")

# Ensure directories exist
os.makedirs(os.path.join(PROCESSED_BASE, "metadata"), exist_ok=True)
os.makedirs(os.path.join(PROCESSED_BASE, "image_metadata"), exist_ok=True)
os.makedirs(os.path.join(PROCESSED_BASE, "registration_data"), exist_ok=True)
os.makedirs(os.path.join(PROCESSED_BASE, "vehicle_master"), exist_ok=True)

# ============================================================
# 1. LOAD PROCESSED FILE METADATA
# ============================================================

if os.path.exists(METADATA_PATH):
    processed_files = set(json.load(open(METADATA_PATH)))
else:
    processed_files = set()
print("Loaded processed files:", processed_files)

# ============================================================
# 2. DETECT ALL FILES IN RAW DIRECTORIES
# ============================================================

def list_all_source_files():
    files = []
    # Registration files (PDFs / images)
    for folder in os.listdir(REG_BASE):
        fpath = os.path.join(REG_BASE, folder)
        if os.path.isdir(fpath):
            for f in os.listdir(fpath):
                full = os.path.join(fpath, f)
                if full.lower().endswith((".jpg", ".pdf")):
                    files.append(full)
    # Checklist CSVs
    for f in os.listdir(CHECKLIST_BASE):
        full = os.path.join(CHECKLIST_BASE, f)
        if full.lower().endswith(".csv"):
            files.append(full)
    return files

all_files = list_all_source_files()
new_files = [f for f in all_files if f not in processed_files]
print("New files to process:", new_files)
if not new_files:
    print("NO NEW FILES — ETL EXITING.")
    exit(0)

# ============================================================
# 3. HELPERS
# ============================================================

def extract_image_metadata(path):
    try:
        img = Image.open(path)
        res = img.size
        return {"file_path": path, "resolution_x": res[0], "resolution_y": res[1], "format": img.format}
    except:
        return {"file_path": path, "resolution_x": None, "resolution_y": None, "format": None}

def ocr_pdf(path):
    try:
        doc = fitz.open(path)
        text = "".join([page.get_text() for page in doc])
        return text
    except:
        return ""

def extract_brand_from_pdf(pdf_text):
    """Extract 'Brand:' from registration PDF text."""
    for line in pdf_text.splitlines():
        if line.lower().startswith("brand:"):
            return line.split(":", 1)[1].strip()
    return "Unknown"

# ============================================================
# 4. PROCESS FILES
# ============================================================

image_rows = []
registration_rows = []
checklist_csv_dfs = []

for file_path in new_files:

    # IMAGES
    if file_path.lower().endswith(".jpg"):
        image_rows.append(extract_image_metadata(file_path))

    # REGISTRATION PDFs
    elif file_path.lower().endswith(".pdf") and "registration" in file_path.lower():
        text = ocr_pdf(file_path)
        vehicle_id = os.path.basename(os.path.dirname(file_path))
        brand = extract_brand_from_pdf(text)
        registration_rows.append({
            "vehicle_id": vehicle_id,
            "file_path": file_path,
            "raw_text": text,
            "vehicle_brand": brand
        })

    # CHECKLIST CSVS
    elif file_path.lower().endswith(".csv"):
        df = pd.read_csv(file_path)
        
        # Extract vehicle_id from filename (handles VH_001.csv or VH_001_checklist.csv)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        parts = filename.split("_")
        if parts[0] == "VH":
            vehicle_id = "_".join(parts[:2])  # VH_001
        else:
            vehicle_id = parts[0]
        df["vehicle_id"] = vehicle_id

        print(f"Loaded CSV for {vehicle_id}, columns: {df.columns.tolist()}, rows: {len(df)}")
        checklist_csv_dfs.append(df)

# ============================================================
# 5. CREATE DATAFRAMES
# ============================================================

image_metadata_df = pd.DataFrame(image_rows)
registration_df = pd.DataFrame(registration_rows)
checklist_df = pd.concat(checklist_csv_dfs, ignore_index=True) if checklist_csv_dfs else pd.DataFrame()

# ============================================================
# 6. CLEAN + UNIFY
# ============================================================

if not checklist_df.empty:
    checklist_df["inspection_date"] = pd.to_datetime(checklist_df.get("inspection_date", pd.Series()))
    checklist_df["vehicle_id"] = checklist_df["vehicle_id"].astype(str).str.strip()

registration_df["vehicle_id"] = registration_df["vehicle_id"].astype(str).str.strip()

# ============================================================
# 7. JOIN VEHICLE DATA
# ============================================================

if not checklist_df.empty:
    vehicle_master_df = registration_df.merge(checklist_df, on="vehicle_id", how="left")
else:
    vehicle_master_df = registration_df.copy()

# Optional: check merge
print("\nSample vehicle_master_df rows:")
print(vehicle_master_df.head())
print(vehicle_master_df.columns.tolist())

# ============================================================
# 8. SAVE OUTPUT TO PROCESSED FOLDER
# ============================================================

image_metadata_df.to_parquet(os.path.join(PROCESSED_BASE, "image_metadata", "image_metadata.parquet"), index=False)
registration_df.to_parquet(os.path.join(PROCESSED_BASE, "registration_data", "registration_data.parquet"), index=False)
vehicle_master_df.to_parquet(os.path.join(PROCESSED_BASE, "vehicle_master", "vehicle_master.parquet"), index=False)

# ============================================================
# 9. UPDATE METADATA
# ============================================================

processed_files.update(new_files)
json.dump(list(processed_files), open(METADATA_PATH, "w"), indent=2)

print("\nETL Complete")
