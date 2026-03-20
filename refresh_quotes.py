import json
import random
import re
from datetime import date

def refresh_quotes():
    # Load quotes
    with open('sozler.json', 'r', encoding='utf-8') as f:
        quotes_list = json.load(f)
    
    # Filter unused quotes
    unused_quotes = [q for q in quotes_list if not q.get('used', False)]
    
    num_quotes_per_day = 3
    
    # If not enough unused quotes, reset all to unused
    if len(unused_quotes) < num_quotes_per_day:
        for q in quotes_list:
            q['used'] = False
        unused_quotes = quotes_list
        print("Not enough unused quotes left. Resetting all quotes to unused.")

    # Select 3 random quotes from the unused pool
    selected = random.sample(unused_quotes, num_quotes_per_day)
    
    # Mark them as used
    selected_texts = []
    for q in selected:
        q['used'] = True
        selected_texts.append(q['text'])

    # Save the updated quotes back to sozler.json
    with open('sozler.json', 'w', encoding='utf-8') as f:
        json.dump(quotes_list, f, ensure_ascii=False, indent=4)
        
    # Format the block
    new_content = "<!-- START_QUOTE -->\n### ⚡ Daily Operational Directives\n"
    for text in selected_texts:
        new_content += f"- > **\"{text}\"**\n"
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
    
    today = date.today()
    print(f"Directives refreshed locally for {today}!")
    for q in selected_texts:
        print(f" - {q}")

if __name__ == "__main__":
    refresh_quotes()
