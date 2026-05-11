import json
import os

try:
    config = json.load(open("config.json"))
    base = config["LOCAL_DATA_PATH"]
except Exception as e:
    print("Config load error:", e)
    exit()

print("Looking for dataset here:")
print(base)

if os.path.exists(base):
    print("✓ Dataset folder FOUND.")
else:
    print("✗ Dataset folder NOT FOUND.")