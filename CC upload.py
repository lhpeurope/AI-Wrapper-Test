import sys
import os
import json
import csv
import requests
from datetime import datetime
from uuid import uuid4

# 🔹 Constants
COMPANY_ID = "24b4b0b6-66f3-4167-8003-2bdde9a9a70c"
LOGIN_URL = "https://v1.cclhp.eu/api/users/login"
DATASET_ID = "654b246f-df17-49c5-b09f-c81ea0080579"
UPLOAD_URL = f"https://v1.cclhp.eu/api/datasets/{DATASET_ID}/upload"
EMAIL = "debug@debug.debug"
PASSWORD = "debug@debug.debug"
CSV_FILE_NAME = (uuid4())
CSV_FILE_PATH = f"/tmp/{CSV_FILE_NAME}.csv"

# 🔹 Function to save JSON as CSV (auto-detect keys)
def save_csv(data_list, file_path):
    if not data_list:
        print("❌ No data to save.")
        return None

    # Auto-detect keys from JSON
    fieldnames = list(data_list[0].keys())

    # Write CSV
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)

    return file_path

# 🔹 Function to get JWT token
def get_jwt_token():
    payload = {"email": EMAIL, "password": PASSWORD}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    response = requests.post(LOGIN_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["proxy_response"]["jwt_token"]
    else:
        print(f"❌ Failed to authenticate: {response.status_code}, {response.text}")
        sys.exit(1)

# 🔹 Function to upload CSV file
def upload_csv(file_path, jwt_token):
    headers = {
        "CCapi-company-id": COMPANY_ID,
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/json"
    }

    with open(file_path, 'rb') as f:
        response = requests.post(UPLOAD_URL, headers=headers, files={'file': f})
    
    if response.status_code == 202:
        print(f"✅ Successfully uploaded {file_path}!")
    else:
        print(f"❌ Upload failed: {response.status_code}, {response.text}")

    os.remove(file_path)

# 🔹 Main function
if __name__ == "__main__":
    input_data = sys.stdin.read().strip()
    
    try:
        # Load and process JSON
        records = json.loads(input_data)

        # Save as CSV dynamically detecting columns
        csv_path = save_csv(records, CSV_FILE_PATH)
        if not csv_path:
            sys.exit(1)

        # Get JWT token
        jwt_token = get_jwt_token()

        # Upload CSV file
        upload_csv(csv_path, jwt_token)

        # Print back processed JSON for NiFi
        print(json.dumps({"status": "success", "csv_path": csv_path}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))