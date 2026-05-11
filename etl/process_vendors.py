import os
import re
import json
import pdfplumber
import pandas as pd
from tqdm import tqdm

# -----------------------------
# CONFIG: set the path to your vendors folder
# Example: "/Users/mishaimamanullah/Downloads/Project_Data_Sample_Final/Vendors"
VENDORS_DIR = "/Users/mishaimamanullah/Downloads/Project_Data_Sample_Final/Vendors"  
# Replace the above path with the actual path on your computer
# -----------------------------

OUTPUT_FILE = "etl/vendor_summary.jsonl"

def extract_payment_amount(pdf_path):
    """Extract AED amount from payment voucher PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "".join([page.extract_text() or "" for page in pdf.pages])

    match = re.search(r"Amount:\s*AED\s*([0-9,]+)", text)
    return float(match.group(1).replace(",", "")) if match else 0.0

def extract_vendor_id_from_soa(pdf_path):
    """Extract vendor ID from SOA PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text() or ""

    match = re.search(r"Vendor\s+(\d+)", text)
    return match.group(1) if match else None

def process_vendor(vendor_folder):
    vendor_path = os.path.join(VENDORS_DIR, vendor_folder)

    job_csv = os.path.join(vendor_path, "job_sheet.csv")
    payment_pdf = os.path.join(vendor_path, "payment_voucher.pdf")
    soa_pdf = os.path.join(vendor_path, "statement_of_accounts.pdf")

    if not os.path.exists(job_csv):
        print(f"Skipping {vendor_folder}, no job_sheet.csv found.")
        return None

    # Read CSV
    df = pd.read_csv(job_csv)
    total_job_amount = df["total_amount"].sum()
    total_hours = df["hours"].sum()
    job_count = len(df)

    # Extract payment amount and vendor ID
    payment_amount = extract_payment_amount(payment_pdf) if os.path.exists(payment_pdf) else 0.0
    vendor_id = extract_vendor_id_from_soa(soa_pdf) if os.path.exists(soa_pdf) else vendor_folder

    return {
    "vendor_id": vendor_id,
    "total_job_amount": float(total_job_amount),
    "payment_amount": float(payment_amount),
    "balance_due": float(total_job_amount - payment_amount)  }

def main():
    if not os.path.exists(VENDORS_DIR):
        print(f"Error: vendors folder not found at {VENDORS_DIR}")
        return

    results = []
    vendor_folders = [f for f in os.listdir(VENDORS_DIR) if os.path.isdir(os.path.join(VENDORS_DIR, f))]

    for folder in tqdm(vendor_folders, desc="Processing Vendors"):
        data = process_vendor(folder)
        if data:
            results.append(data)

    os.makedirs("etl", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    print(f"ETL complete! Created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
