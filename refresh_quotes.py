import json
import random
import re
from datetime import date

def refresh_quotes():
    # Load quotes
    with open('sozler.json', 'r', encoding='utf-8') as f:
        quotes_list = json.load(f)
    
    # Sort quotes alphabetically to ensure consistent absolute ordering before shuffling
    quotes_list.sort()
    
    # Create a reproducible shuffle using a fixed seed
    # This ensures the list is always scrambled in the same way, mixing authors
    r = random.Random(42)  # Change 42 to another number to completely re-scramble
    r.shuffle(quotes_list)
    
    # Calculate how many days have passed since a fixed epoch (e.g., Jan 1, 2024)
    epoch = date(2024, 1, 1)
    today = date.today()
    days_passed = (today - epoch).days
    
    # We select 5 quotes per day. 
    # Use days_passed to slide the window across the shuffled list.
    total_quotes = len(quotes_list)
    num_quotes_per_day = 5
    
    start_index = (days_passed * num_quotes_per_day) % total_quotes
    
    selected = []
    for i in range(num_quotes_per_day):
        idx = (start_index + i) % total_quotes
        selected.append(quotes_list[idx])
    
    # Format the block
    new_content = "<!-- START_QUOTE -->\n### ⚡ Daily Operational Directives\n"
    for q in selected:
        new_content += f"- > **\"{q}\"**\n"
    new_content += "<!-- END_QUOTE -->"
    
    # Read README
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
    
    # Replace content between markers
    pattern = r"<!-- START_QUOTE -->.*?<!-- END_QUOTE -->"
    updated_readme = re.sub(pattern, new_content, readme, flags=re.DOTALL)
    
    # Write back to README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(updated_readme)
    
    print(f"Directives refreshed locally for {today} (Day: {days_passed})!")
    for q in selected:
        print(f" - {q}")

if __name__ == "__main__":
    refresh_quotes()
