import os
import re
import pandas as pd
import numpy as np


def load_processed_voucher_text():
    """
    Loads the processed parquet that contains:
      - vendor_id
      - voucher_file
      - raw_text
    """
    processed_path = os.path.join(
        "processed", "vendors", "voucher_text", "pair2_voucher_text.parquet"
    )
    if not os.path.isfile(processed_path):
        raise FileNotFoundError(
            f"Processed parquet not found at {processed_path}. "
            "Run pair2_vouchers_etl.py first."
        )

    df = pd.read_parquet(processed_path)
    return df


def parse_amount(text: str):
    """
    Extracts the numeric amount from a line like:
        'Amount: AED 20,000'
    Returns a float (e.g. 20000.0) or NaN if nothing found.
    """
    if not isinstance(text, str):
        return np.nan

    # Look for 'Amount:' followed by 'AED' and a number with optional commas and decimals
    match = re.search(
        r"Amount\s*:\s*AED\s*([\d,]+(?:\.\d{1,2})?)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return np.nan

    amount_str = match.group(1)  # e.g. '20,000' or '20000.50'
    amount_str = amount_str.replace(",", "")
    try:
        return float(amount_str)
    except ValueError:
        return np.nan


def build_curated_table(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the raw voucher text DataFrame and returns a curated DataFrame with:
      - vendor_id
      - voucher_file
      - raw_text
      - invoice_amount
      - missing_amount (bool)
      - is_extreme (bool)
    """
    df = df_raw.copy()

    # 1. Parse amount
    df["invoice_amount"] = df["raw_text"].apply(parse_amount)

    # 2. Missing amount flag
    df["missing_amount"] = df["invoice_amount"].isna()

    # 3. Extreme amount flag
    # Use mean + 3 * std as a simple heuristic
    valid_amounts = df["invoice_amount"].dropna()
    if len(valid_amounts) > 0:
        mean_val = valid_amounts.mean()
        std_val = valid_amounts.std(ddof=0)
        threshold = mean_val + 3 * std_val
        df["is_extreme"] = df["invoice_amount"] > threshold
    else:
        # If no valid amounts, no extremes
        df["is_extreme"] = False

    return df


def save_curated_outputs(df_curated: pd.DataFrame):
    """
    Saves:
      - full curated table to curated_data/pair2_vouchers.parquet
      - issue-only table to curated_data/pair2_voucher_issues.parquet
    """
    curated_dir = "curated_data"
    os.makedirs(curated_dir, exist_ok=True)

    full_path = os.path.join(curated_dir, "pair2_vouchers.parquet")
    df_curated.to_parquet(full_path, index=False)
    print(f"Saved curated vouchers to: {full_path}")

    # Build issues table: either missing amount or extreme
    issues_df = df_curated[
        (df_curated["missing_amount"]) | (df_curated["is_extreme"])
    ].copy()

    issues_path = os.path.join(curated_dir, "pair2_voucher_issues.parquet")
    issues_df.to_parquet(issues_path, index=False)
    print(f"Saved voucher issues to: {issues_path}")


def main():
    # 1. Load processed text
    df_raw = load_processed_voucher_text()
    print("Loaded raw voucher text:", df_raw.shape)

    # 2. Build curated table with parsed fields and flags
    df_curated = build_curated_table(df_raw)
    print("Curated DataFrame shape:", df_curated.shape)
    print(
        df_curated[
            ["vendor_id", "voucher_file", "invoice_amount",
             "missing_amount", "is_extreme"]
        ].head()
    )

    # 3. Save outputs
    save_curated_outputs(df_curated)


if __name__ == "__main__":
    main()
