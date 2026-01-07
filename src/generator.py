import csv
import random
import os
import time
from faker import Faker
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# This path matches the volume mapped in docker-compose.yml
# We write to ./data/raw locally, which Docker sees as /data/raw
DATA_DIR = "./data/raw"  
RECORDS_COUNT = 5000     
fake = Faker()

def ensure_directory():
    """Make sure the folder exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"[INFO] Created directory: {DATA_DIR}")

def generate_cdr():
    """Generates a CSV file simulating Call Detail Records."""
    ensure_directory()
    
    # Generate a filename with timestamp (e.g., cdr_20240101_120000.csv)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DATA_DIR}/cdr_{timestamp_str}.csv"
    
    print(f"[INFO] Generating {RECORDS_COUNT} records...")
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # HEADER: Standard Telecom Columns
        # call_id: Unique ID
        # caller_num / receiver_num: Phone numbers
        # call_type: VOICE, SMS, or DATA
        # duration_sec: Length of call
        # timestamp: When it happened
        # tower_id: Which cell tower handled it
        # signal_strength: 1-5 bars
        writer.writerow(['call_id', 'caller_num', 'receiver_num', 'call_type', 'duration_sec', 'timestamp', 'tower_id', 'signal_strength'])
        
        tower_ids = [f"TOWER_{i:03d}" for i in range(1, 51)] # 50 Towers
        
        for _ in range(RECORDS_COUNT):
            call_id = fake.uuid4()
            caller = f"+947{random.randint(10000000, 99999999)}"
            receiver = f"+947{random.randint(10000000, 99999999)}"
            call_type = random.choice(['VOICE', 'VOICE', 'VOICE', 'SMS', 'DATA']) # Weighted: Mostly voice
            duration = random.randint(5, 1200) if call_type == 'VOICE' else 0
            
            # Random time in the last 24 hours
            call_time = datetime.now() - timedelta(minutes=random.randint(0, 1440))
            ts = call_time.strftime("%Y-%m-%d %H:%M:%S")
            
            tower = random.choice(tower_ids)
            signal = random.randint(1, 5) # 1 (Weak) to 5 (Strong)
            
            writer.writerow([call_id, caller, receiver, call_type, duration, ts, tower, signal])
            
    print(f"[SUCCESS] Data generated at: {filename}")

if __name__ == "__main__":
    generate_cdr()