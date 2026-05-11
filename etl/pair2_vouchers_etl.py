import os
import json
import glob

import PyPDF2
import pandas as pd


def load_config():
    """
    Reads config.json from the project root
    and returns it as a Python dict.
    """
    with open("config.json", "r") as f:
        config = json.load(f)
    return config


def get_vendors_path(config):
    """
    Builds the full path to the Vendors folder
    using LOCAL_DATA_PATH from config.json.
    Example:
      LOCAL_DATA_PATH = C:/.../Project_Data_Sample_Final
      Vendors path    = C:/.../Project_Data_Sample_Final/Vendors
    """
    base_path = config["LOCAL_DATA_PATH"]
    vendors_path = os.path.join(base_path, "Vendors")
    return vendors_path


def find_payment_vouchers(vendors_path):
    """
    Looks through all Vendor_xxx folders under Vendors
    and finds files named like 'payment_voucher.*'.
    Returns a list of (vendor_id, file_path).
    """
    results = []

    if not os.path.isdir(vendors_path):
        print("ERROR: Vendors folder does NOT exist:", vendors_path)
        return results

    # Example vendor folders: Vendor_001, Vendor_002, ...
    vendor_folders = sorted(
        d for d in glob.glob(os.path.join(vendors_path, "Vendor_*"))
        if os.path.isdir(d)
    )

    print(f"Found {len(vendor_folders)} vendor folders under Vendors.")

    for vendor_dir in vendor_folders:
        vendor_name = os.path.basename(vendor_dir)  # e.g. 'Vendor_012'

        # Look for files that start with 'payment_voucher'
        pattern = os.path.join(vendor_dir, "payment_voucher*")
        voucher_files = glob.glob(pattern)

        if not voucher_files:
            # Some vendors may not have a payment_voucher file
            continue

        for fpath in voucher_files:
            results.append((vendor_name, fpath))

    return results


def extract_text_from_pdf(pdf_path):
    """
    Reads all pages of a PDF using PyPDF2 and returns
    the combined text as a single string.
    If anything goes wrong, returns an empty string.
    """
    try:
        text_pieces = []

        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            for page in reader.pages:
                page_text = page.extract_text() or ""
                text_pieces.append(page_text)

        full_text = "\n".join(text_pieces).strip()
        return full_text

    except Exception as e:
        print(f"ERROR reading {pdf_path}: {e}")
        return ""


def main():
    # 1. Load config.json and paths
    config = load_config()
    vendors_path = get_vendors_path(config)
    print("Vendors folder path:", vendors_path)

    # 2. Find all payment_voucher files
    vouchers = find_payment_vouchers(vendors_path)
    print(f"Total payment_voucher files found: {len(vouchers)}")

    if not vouchers:
        print("No vouchers found, nothing to do.")
        return

    # 3. Extract text for each voucher and build rows for a table
    rows = []

    for vendor_name, fpath in vouchers:
        file_name = os.path.basename(fpath)  # 'payment_voucher.pdf'
        print(f"Reading {vendor_name}: {file_name}")

        raw_text = extract_text_from_pdf(fpath)

        rows.append(
            {
                "vendor_id": vendor_name,
                "voucher_file": file_name,   # cleaner: just the filename
                "raw_text": raw_text,
            }
        )

    # 4. Convert to a pandas DataFrame
    df = pd.DataFrame(rows)
    print("\nDataFrame shape:", df.shape)
    print(df.head(3))

    # 5. Ensure output folders exist
    processed_dir = os.path.join("processed", "vendors", "voucher_text")
    os.makedirs(processed_dir, exist_ok=True)

    integration_dir = "integration_samples"
    os.makedirs(integration_dir, exist_ok=True)

    # 6. Save the full raw-text table as Parquet (processed layer)
    processed_out_path = os.path.join(
        processed_dir, "pair2_voucher_text.parquet"
    )
    df.to_parquet(processed_out_path, index=False)
    print(f"\nSaved full voucher text to: {processed_out_path}")

    # 7. Save 3–5 sample rows for integration_samples (for Pair 5)
    sample_df = df.head(5)
    sample_out_path = os.path.join(
        integration_dir, "vouchers_sample.parquet"
    )
    sample_df.to_parquet(sample_out_path, index=False)
    print(f"Saved sample vouchers to: {sample_out_path}")


if __name__ == "__main__":
    main()
