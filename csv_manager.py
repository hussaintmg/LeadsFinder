import pandas as pd
import os
import glob
from datetime import datetime

CSV_DIR = "c:/Coding/agent/ai_client_agent/runs/"

def save_to_new_csv(leads):
    if not os.path.exists(CSV_DIR):
        os.makedirs(CSV_DIR)
        
    # Determine the next run number
    existing_files = glob.glob(os.path.join(CSV_DIR, "leads_run_*.csv"))
    run_numbers = []
    for f in existing_files:
        try:
            num = int(os.path.basename(f).replace("leads_run_", "").replace(".csv", ""))
            run_numbers.append(num)
        except:
            continue
    
    next_run = max(run_numbers) + 1 if run_numbers else 1
    filename = f"leads_run_{next_run}.csv"
    filepath = os.path.join(CSV_DIR, filename)
    
    df = pd.DataFrame(leads)
    df.to_csv(filepath, index=False)
    return filepath

def get_all_runs():
    if not os.path.exists(CSV_DIR):
        return []
    
    files = glob.glob(os.path.join(CSV_DIR, "leads_run_*.csv"))
    # Sort by run number descending
    files.sort(key=lambda x: int(os.path.basename(x).replace("leads_run_", "").replace(".csv", "")), reverse=True)
    return files

def update_csv_field(filepath, company_name, field, value):
    df = pd.read_csv(filepath)
    df.loc[df['company_name'] == company_name, field] = value
    df.to_csv(filepath, index=False)
