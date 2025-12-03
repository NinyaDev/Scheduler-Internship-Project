import pandas as pd
import random

# --- CONFIGURATION ---
NUM_STUDENTS = 15
# We assume the Help Desk is open 8am - 6pm (10 hours)
SHIFTS = [f"{h}:00" for h in range(8, 18)]
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

names = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", 
    "Riley", "Jamie", "Dakota", "Cameron", "Avery",
    "Quinn", "Hayden", "Sam", "Charlie", "Peyton"
]

# --- GENERATE DATA ---
data = []

for i in range(NUM_STUDENTS):
    student_row = {'Name': names[i]}
    
    # Randomly assign a "Max Hours" cap (mostly 20, some less)
    student_row['Max_Hours'] = random.choice([10, 15, 20, 20, 20])
    
    # For each day, simulate class schedules
    # 1 = Available to work, 0 = In Class
    for day in DAYS:
        # Create a pattern: Students usually have blocks of classes
        # Let's say they are available for 60% of the day roughly
        daily_availability = []
        for time in SHIFTS:
            # 70% chance they are free at any given hour
            is_free = 1 if random.random() > 0.3 else 0
            student_row[f"{day}_{time}"] = is_free
            
    data.append(student_row)

# --- SAVE TO EXCEL ---
df = pd.DataFrame(data)

# We save as CSV because it's easier to inspect, but you could use .xlsx too
filename = "student_availability.csv"
df.to_csv(filename, index=False)

print(f"✅ Successfully created {filename}")
print("Open this file in Excel to see what your 'Standardized Input' looks like.")