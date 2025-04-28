import csv
from datetime import datetime

def parse_french_date(date_str):
    """Convert '9 mai 2025' to datetime object"""
    day, month, year = date_str.split()
    month_map = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }
    return datetime(int(year), month_map[month.lower()], int(day))

def merge_and_sort():
    # Initialize merged data
    merged = []
    
    # Define input files
    files = ['ChM_matches_1.csv', 'ChM_matches_2.csv']
    
    # Load and merge data
    for file in files:
        try:
            with open(file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                merged.extend(list(reader))
        except FileNotFoundError:
            print(f"⚠️ Warning: {file} not found")
    
    # Sort by date
    merged.sort(key=lambda x: parse_french_date(x['date']))
    
    # Write merged file
    with open('ChM_matches_merged.csv', mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(merged)
    
    print(f"Successfully merged {len(merged)} matches")

if __name__ == "__main__":
    merge_and_sort()
