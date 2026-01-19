import json
import random
import re
import os

def refresh_quotes():
    # Load quotes
    with open('sozler.json', 'r', encoding='utf-8') as f:
        quotes_list = json.load(f)
    
    # Select 3 random quotes
    selected = random.sample(quotes_list, 3)
    
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
    
    print("Directives refreshed locally!")
    for q in selected:
        print(f" - {q}")

if __name__ == "__main__":
    refresh_quotes()
