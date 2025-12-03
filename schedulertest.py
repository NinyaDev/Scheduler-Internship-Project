import pandas as pd

# --- CONFIGURATION ---
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
SHIFTS = [f"{h}:00" for h in range(8, 18)] # 8 AM to 6 PM

# Location Constraints
LOCATIONS = {
    'Bristlecone': {'min': 1, 'max': 1},
    'Library': {'min': 1, 'max': 2},
    'Main Desk': {'min': 2, 'max': 10}
}

# --- MOCK DATA (Student "Static" Availability) ---
# 1 = Available, 0 = Class/Busy
# In your real app, you'd load this from an Excel sheet
students = [
    {'name': 'Alex',  'max_hours': 20, 'assigned': 0, 'avail': {'Monday': ['8:00', '9:00', '10:00'], 'Wednesday': ['8:00', '9:00', '10:00']}},
    {'name': 'Sarah', 'max_hours': 20, 'assigned': 0, 'avail': {'Monday': SHIFTS, 'Tuesday': SHIFTS, 'Wednesday': SHIFTS}}, # Open availability
    {'name': 'Mike',  'max_hours': 20, 'assigned': 0, 'avail': {'Tuesday': ['12:00', '13:00', '14:00'], 'Thursday': ['12:00', '13:00']}},
    {'name': 'Emma',  'max_hours': 20, 'assigned': 0, 'avail': {'Monday': ['14:00', '15:00', '16:00'], 'Wednesday': ['14:00', '15:00', '16:00']}},
]

final_schedule = []

print("--- BUILDING MASTER SCHEDULE ---")

for day in DAYS:
    for time in SHIFTS:
        # Who is free right now?
        available_students = [s for s in students if day in s['avail'] and time in s['avail'][day]]
        
        # Sort them by who needs hours most (Fairness logic)
        # We prefer people who have low assigned hours so far
        available_students.sort(key=lambda x: x['assigned'])
        
        staff_at_bristlecone = []
        staff_at_library = []
        staff_at_main = []
        
        for student in available_students:
            if student['assigned'] >= student['max_hours']:
                continue
            
            # 1. Fill Bristlecone (Hardest to fill)
            if len(staff_at_bristlecone) < LOCATIONS['Bristlecone']['min']:
                staff_at_bristlecone.append(student['name'])
                student['assigned'] += 1
                
            # 2. Fill Library
            elif len(staff_at_library) < LOCATIONS['Library']['min']:
                staff_at_library.append(student['name'])
                student['assigned'] += 1
                
            # 3. Fill Main Desk (High Capacity)
            elif len(staff_at_main) < LOCATIONS['Main Desk']['max']:
                staff_at_main.append(student['name'])
                student['assigned'] += 1
        
        # Add to Master Schedule
        final_schedule.append({
            'Day': day,
            'Time': time,
            'Bristlecone': ", ".join(staff_at_bristlecone),
            'Library': ", ".join(staff_at_library),
            'Main Desk': ", ".join(staff_at_main)
        })

# Output for review
df = pd.DataFrame(final_schedule)
print(df.head(15)) # Prints first few rows