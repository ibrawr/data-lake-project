import os
import json
import pandas as pd

# ============================================================
# CONFIG
# ============================================================
CURATED_DIR = "curated"
METADATA_PATH = "processed/metadata/processed_files.json"
VEHICLE_MASTER_PATH = os.path.join("processed", "vehicle_master", "vehicle_master.parquet")

# ============================================================
# 1. LOAD METADATA
# ============================================================
if os.path.exists(METADATA_PATH):
    processed_files = json.load(open(METADATA_PATH))
else:
    processed_files = []

print(f"Total processed files: {len(processed_files)}")

# ============================================================
# 2. LOAD VEHICLE MASTER DATA
# ============================================================
vehicle_master_df = pd.read_parquet(VEHICLE_MASTER_PATH) if os.path.exists(VEHICLE_MASTER_PATH) else pd.DataFrame()

# ============================================================
# 3. HELPER FUNCTION
# ============================================================
def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else 0

# Weights for reliability calculation
WEIGHTS = {
    "engine_failures": 1.5,   # engine is most critical
    "brake_failures": 1.2,    # brakes are important
    "tire_failures": 1.0,     # tires moderate
    "lights_failures": 0.5    # lights least critical
}

# ============================================================
# 4. VEHICLE-LEVEL MAINTENANCE METRICS
# ============================================================
if not vehicle_master_df.empty:
    maintenance_summary = []

    for vehicle_id, group in vehicle_master_df.groupby("vehicle_id"):
        tire_failures = group.get("tires", pd.Series()).eq("Fail").sum()
        brake_failures = group.get("brakes", pd.Series()).eq("Fail").sum()
        engine_failures = group.get("engine", pd.Series()).eq("Fail").sum()
        lights_failures = group.get("lights", pd.Series()).eq("Fail").sum()
        num_inspections = len(group)

        # Standardized failures per inspection
        tire_std = safe_divide(tire_failures, num_inspections)
        brake_std = safe_divide(brake_failures, num_inspections)
        engine_std = safe_divide(engine_failures, num_inspections)
        lights_std = safe_divide(lights_failures, num_inspections)

        # Weighted reliability (engine > brakes > tires > lights)
        weighted_failures = (
            engine_std * WEIGHTS["engine_failures"] +
            brake_std * WEIGHTS["brake_failures"] +
            tire_std * WEIGHTS["tire_failures"] +
            lights_std * WEIGHTS["lights_failures"]
        )
        reliability_score = 1 / (1 + weighted_failures)

        maintenance_summary.append({
            "vehicle_id": vehicle_id,
            "vehicle_brand": group.get("vehicle_brand", pd.Series(["Unknown"])).iloc[0],
            "tire_failures": tire_failures,
            "brake_failures": brake_failures,
            "engine_failures": engine_failures,
            "lights_failures": lights_failures,
            "num_inspections": num_inspections,
            "tire_failures_per_inspection": tire_std,
            "brake_failures_per_inspection": brake_std,
            "engine_failures_per_inspection": engine_std,
            "lights_failures_per_inspection": lights_std,
            "total_failures_per_inspection": tire_std + brake_std + engine_std + lights_std,
            "reliability_score": reliability_score
        })

    maintenance_df = pd.DataFrame(maintenance_summary)

    # Top 5 most dangerous vehicles (lowest weighted reliability)
    top_5_dangerous = maintenance_df.sort_values(by="reliability_score").head(5)

# ============================================================
# 5. BRAND-LEVEL MAINTENANCE METRICS (STANDARDIZED + WEIGHTED)
# ============================================================
if not maintenance_df.empty:
    brand_summary = maintenance_df.groupby("vehicle_brand")[[
        "tire_failures_per_inspection",
        "brake_failures_per_inspection",
        "engine_failures_per_inspection",
        "lights_failures_per_inspection"
    ]].mean().reset_index()

    # Total failures per inspection per brand
    brand_summary["total_failures_per_inspection"] = (
        brand_summary["tire_failures_per_inspection"] +
        brand_summary["brake_failures_per_inspection"] +
        brand_summary["engine_failures_per_inspection"] +
        brand_summary["lights_failures_per_inspection"]
    )

    # Weighted reliability per brand
    brand_summary["reliability_score"] = 1 / (
        1 + (
            brand_summary["engine_failures_per_inspection"] * WEIGHTS["engine_failures"] +
            brand_summary["brake_failures_per_inspection"] * WEIGHTS["brake_failures"] +
            brand_summary["tire_failures_per_inspection"] * WEIGHTS["tire_failures"] +
            brand_summary["lights_failures_per_inspection"] * WEIGHTS["lights_failures"]
        )
    )

    # Sort brands by reliability score (worst first)
    vehicle_maintenance = brand_summary.sort_values(by="reliability_score")

# ============================================================
# 6. DISPLAY TABLES
# ============================================================
print("\n--- Brand-Level Vehicle Maintenance Summary (Standardized + Weighted Reliability) ---")
print(vehicle_maintenance)

print("\n--- Vehicles To Look Out For (Top 5 Most Dangerous) ---")
print(top_5_dangerous[[
    "vehicle_id", "vehicle_brand", "tire_failures", "brake_failures",
    "engine_failures", "lights_failures", "num_inspections",
    "total_failures_per_inspection", "reliability_score"
]])

# ============================================================
# 7. SAVE OUTPUT TO PARQUET
# ============================================================
analytics_dir = os.path.join(CURATED_DIR, "analytics")
os.makedirs(analytics_dir, exist_ok=True)

maintenance_df.to_parquet(os.path.join(analytics_dir, "vehicle_level_maintenance.parquet"), index=False)
vehicle_maintenance.to_parquet(os.path.join(analytics_dir, "brand_level_maintenance.parquet"), index=False)

print(f"\nVehicle-level analytics saved to '{analytics_dir}/vehicle_level_maintenance.parquet'")
print(f"Brand-level analytics saved to '{analytics_dir}/brand_level_maintenance.parquet'")
