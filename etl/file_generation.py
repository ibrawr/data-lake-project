import os
import random
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image
from fpdf import FPDF

# ============================================================
# CONFIG
# ============================================================

NUM_VEHICLES = 60
VEHICLE_IDS = [f"VH_{str(i).zfill(3)}" for i in range(1, NUM_VEHICLES + 1)]

REG_BASE = "raw/Vehicle_Registration"
CHECKLIST_BASE = "raw/Vehicle_Checklist"
LOGOS_DIR = "logos"

BRANDS = ["toyota", "honda", "hyundai", "volvo", "mercedes"]

os.makedirs(REG_BASE, exist_ok=True)
os.makedirs(CHECKLIST_BASE, exist_ok=True)

# Collect logos for the 5 brands
brand_logos = {}
for brand in BRANDS:
    logo_file = os.path.join(LOGOS_DIR, f"{brand}.png")
    if os.path.exists(logo_file):
        brand_logos[brand] = logo_file
if not brand_logos:
    raise ValueError("No logos found in logos/ folder for the 5 brands!")

# ============================================================
# 1. CREATE SYNTHETIC CHECKLIST CSV PER VEHICLE (REALISTIC)
# ============================================================

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)

for vehicle in VEHICLE_IDS:
    rows = []
    num_inspections = random.randint(1, 10)  # random number of inspections per vehicle
    for _ in range(num_inspections):
        # Pick a random date between start_date and end_date
        random_days = random.randint(0, (end_date - start_date).days)
        date = start_date + timedelta(days=random_days)

        rows.append({
            "vehicle_id": vehicle,
            "inspection_date": date.strftime("%Y-%m-%d"),
            "tires": random.choices(["Pass", "Fail"], weights=[0.9, 0.1])[0],
            "brakes": random.choices(["Pass", "Fail"], weights=[0.8, 0.2])[0],
            "engine": random.choices(["Pass", "Fail"], weights=[0.95, 0.05])[0],
            "lights": random.choices(["Pass", "Fail"], weights=[0.7, 0.3])[0]
        })
    
    # Sort rows by date for realism
    rows.sort(key=lambda x: x["inspection_date"])
    
    # Save CSV per vehicle
    csv_path = os.path.join(CHECKLIST_BASE, f"{vehicle}_checklist.csv")
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"Created checklist CSV: {csv_path}")

# ============================================================
# 2. CREATE SYNTHETIC REGISTRATION PDFs
# ============================================================

vehicle_brands = {}  # Save which brand each vehicle has

for vehicle in VEHICLE_IDS:
    vehicle_dir = os.path.join(REG_BASE, vehicle)
    os.makedirs(vehicle_dir, exist_ok=True)
    
    # Pick a random brand
    brand_name = random.choice(BRANDS)
    vehicle_brands[vehicle] = brand_name
    
    pdf_path = os.path.join(vehicle_dir, "registration_card.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Vehicle ID: {vehicle}", ln=True)
    pdf.cell(0, 10, f"License Plate: {vehicle}_LP{random.randint(100,999)}", ln=True)
    pdf.cell(0, 10, f"Engine Number: EN{random.randint(1000,9999)}", ln=True)
    pdf.cell(0, 10, f"Owner: Owner_{random.randint(1, 50)}", ln=True)
    pdf.cell(0, 10, f"Brand: {brand_name.capitalize()}", ln=True)  # Save brand here
    pdf.output(pdf_path)
    print(f"Created registration PDF: {pdf_path}")

# ============================================================
# 3. CREATE VEHICLE IMAGES
# ============================================================

for vehicle in VEHICLE_IDS:
    vehicle_dir = os.path.join(REG_BASE, vehicle)
    
    brand_name = vehicle_brands[vehicle]
    logo_path = brand_logos[brand_name]
    
    for view in ["front", "back", "left", "right"]:
        img_path = os.path.join(vehicle_dir, f"{view}.jpg")
        img = Image.new(
            "RGB", 
            (800, 600), 
            color=(random.randint(0,255), random.randint(0,255), random.randint(0,255))
        )
        
        # Only front view gets the logo
        if view == "front":
            logo = Image.open(logo_path).convert("RGBA")
            
            # Scale logo to fit the image without stretching
            max_logo_width = img.width // 2
            max_logo_height = img.height // 2
            logo_ratio = min(max_logo_width / logo.width, max_logo_height / logo.height)
            logo_width = int(logo.width * logo_ratio)
            logo_height = int(logo.height * logo_ratio)
            logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            
            # Paste centered
            img.paste(logo, ((img.width - logo_width)//2, (img.height - logo_height)//2), logo)
        
        img.save(img_path)
        print(f"Created {view} image for {vehicle} ({'with logo' if view=='front' else 'placeholder'})")

print("\nSynthetic dataset generation complete!")
