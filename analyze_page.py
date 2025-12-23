from bs4 import BeautifulSoup
import re

with open('page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

script_tags = soup.find_all('script')

found_data = False
for script in script_tags:
    if script.string:  # Inline script
        # Look for patterns that might indicate talent data (e.g., JSON objects, large arrays)
        # It's common for talent data to be in a global variable or within a function call
        if 'talents' in script.string.lower() or 'specs' in script.string.lower() or 'tree' in script.string.lower():
            print(f"--- Inline Script Content (potential data) ---")
            print(script.string[:1000]) # Print first 1000 characters to avoid huge output
            found_data = True
            # Attempt to extract JSON-like structures
            json_match = re.search(r'[\[\s*\{.*?\}\s*\]]', script.string, re.DOTALL)
            if json_match:
                print(f"\n--- Found JSON-like structure in inline script ---")
                print(json_match.group(0)[:1000])
                # Save to a temporary file for further inspection
                with open('temp_talent_data.js', 'w', encoding='utf-8') as temp_f:
                    temp_f.write(json_match.group(0))
                print("Saved potential JSON data to temp_talent_data.js")
                
            json_match_obj = re.search(r'{\s*".*?":\s*\[.*?\]', script.string, re.DOTALL)
            if json_match_obj:
                print(f"\n--- Found JSON Object-like structure in inline script ---")
                print(json_match_obj.group(0)[:1000])
                with open('temp_talent_data_obj.js', 'w', encoding='utf-8') as temp_f:
                    temp_f.write(json_match_obj.group(0))
                print("Saved potential JSON object data to temp_talent_data_obj.js")

    elif script.get('src'): # External script
        print(f"--- External Script: {script.get('src')} ---")

if not found_data:
    print("No obvious talent data found in script tags. Further manual inspection might be needed.")
