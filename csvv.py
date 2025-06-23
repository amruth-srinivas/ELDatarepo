import pandas as pd
import random
from datetime import datetime, timedelta

# Headers taken from DataLog2025-01.csv
headers = [
    'Cell(title)', 'Comment(EFF)', 'User', 'Ref', 'ID', 'Date', 'Time',
    'Module type', 'Pmax', 'FF', 'Voc', 'Isc', 'Vpmax', 'Ipmax', 'Irr',
    'CIrr', 'TMod', 'CTMod', 'Rs', 'Rsh', 'CellEff', 'ModEff', 'LTI',
    'PN', 'ClassBin', 'MeasStat', 'MachStat'
]

# Function to generate dummy values for each column
def generate_dummy_row():
    base_date = datetime.now()
    return {
        'Cell(title)': f"PR{random.randint(1000,9999)}D{random.randint(1,9)}",
        'Comment(EFF)': f"EFF-{round(random.uniform(18, 23), 2)}%",
        'User': f"{random.randint(100000,999999)}AB",
        'Ref': f"I5{random.randint(100000,999999)}{random.choice(['A', 'B'])}",
        'ID': f"{random.randint(1000,9999)}",
        'Date': base_date.strftime("%d-%m-%Y"),
        'Time': base_date.strftime("%H:%M:%S"),
        'Module type': random.choice(["Low Power", "Medium Power", "High Power"]),
        'Pmax': round(random.uniform(400, 600), 3),
        'FF': round(random.uniform(0.7, 0.85), 6),
        'Voc': round(random.uniform(30, 55), 6),
        'Isc': round(random.uniform(8, 15), 6),
        'Vpmax': round(random.uniform(25, 45), 6),
        'Ipmax': round(random.uniform(7, 14), 6),
        'Irr': round(random.uniform(800, 1000), 6),
        'CIrr': 1000,
        'TMod': round(random.uniform(25, 35), 1),
        'CTMod': 25,
        'Rs': round(random.uniform(0.1, 0.3), 5),
        'Rsh': round(random.uniform(200, 400), 5),
        'CellEff': round(random.uniform(19, 22), 6),
        'ModEff': 40,
        'LTI': random.choice(["Isc-Voc", "Constant"]),
        'PN': random.choice(["Linear IV", "Step IV"]),
        'ClassBin': random.choice(["yes", "no"]),
        'MeasStat': round(random.uniform(0.0001, 0.001), 6),
        'MachStat': round(random.uniform(0.1, 0.3), 7),
    }

# Number of dummy rows
num_rows = 100

# Generate dummy data
data = [generate_dummy_row() for _ in range(num_rows)]

# Create DataFrame and save to CSV
df_dummy = pd.DataFrame(data)
df_dummy.to_csv("D:\\csv\\DataLog.csv", index=False)

print("Data Log CSV file 'DataLog.csv' created successfully.")
