from bs4 import BeautifulSoup
import json
import sys
import re

def extract_talents_with_structure(html_file_path, class_name):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Final structured data
    final_structured_talents = {class_name: {}}

    # Find the main container for all talent trees (3 columns)
    # Looking for a div that contains the three h2 elements for tree names
    main_wrapper = soup.find('div', class_='flex flex-col md:flex-row gap-4') # This seems to be the wrapper on current site

    if not main_wrapper:
        main_wrapper = soup.find('div', class_='flex justify-center flex-wrap') # Fallback
    
    if not main_wrapper:
        print(f"Error: Could not find main talent container for {class_name}. Cannot extract tree/tier structure.")
        return {}


    tree_columns = main_wrapper.find_all('div', class_='flex flex-col w-[300px]') # These are the actual columns
    
    if not tree_columns or len(tree_columns) != 3:
        print(f"Error: Could not find 3 talent tree columns for {class_name}. Found: {len(tree_columns)}")
        return {}

    # Iterate through each talent tree column
    for tree_idx, tree_col_div in enumerate(tree_columns):
        tree_name_tag = tree_col_div.find('h2', class_='text-3xl') 
        current_tree_name = tree_name_tag.get_text(strip=True) if tree_name_tag else f"Unknown Tree {tree_idx + 1}"
        final_structured_talents[class_name][current_tree_name] = {}

        # Talents are inside a grid structure within each column
        talent_grid = tree_col_div.find('div', class_='grid grid-cols-4 gap-2')
        if not talent_grid:
            print(f"Warning: Could not find talent grid for {current_tree_name} tree.")
            continue
        
        # Each child of the talent_grid is a talent slot or an empty slot.
        # We need to map these to tiers. Assuming 4 columns, a row index will be floor(index / 4)
        talent_slot_elements = talent_grid.find_all('div', class_=lambda c: c and ('relative' in c or 'h-16' in c or 'h-32' in c)) # Find all grid cells

        talents_in_tree = {}

        for slot_idx, slot_div in enumerate(talent_slot_elements):
            talent_button = slot_div.find('button', attrs={'data-tippy-content': True})
            if not talent_button:
                continue # Skip empty slots or non-talent elements

            button_tippy_content = talent_button.get('data-tippy-content')
            if not button_tippy_content:
                continue

            tippy_soup = BeautifulSoup(button_tippy_content, 'html.parser')
            
            name_tag = tippy_soup.find('h4', class_='tw-color')
            rank_tag = tippy_soup.find('p', class_='font-bold')
            desc_tag = tippy_soup.find('p', class_='whitespace-pre-wrap')
            
            if not (name_tag and rank_tag and desc_tag):
                continue # Malformed tooltip, skip

            name = name_tag.get_text(strip=True)
            description = desc_tag.get_text(strip=True)
            rank_str = rank_tag.get_text(strip=True)
            
            max_rank = 1
            if '/' in rank_str:
                try:
                    parts = rank_str.split('/')
                    if len(parts) == 2:
                        max_rank = int(parts[1])
                except ValueError:
                    pass
            
            level_req = 10 # Default
            # Search for level requirement anywhere in the tooltip's text
            tooltip_full_text = tippy_soup.get_text(separator=' ', strip=True)
            match_level = re.search(r'Requires level (\d+)', tooltip_full_text)
            if match_level:
                level_req = int(match_level.group(1))
            
            talent_tier = (slot_idx // 4) + 1 # Assuming 4 columns per grid row, tier is 1-indexed
            
            # Prerequisite extraction from description: "Requires TalentName (Rank X)"
            prerequisites = []
            talent_prereq_matches = re.finditer(r'Requires\s+([A-Za-z0-9\s\':-]+?)\s+\(Rank\s+(\d+)\)', description)
            for match in talent_prereq_matches:
                prereq_name = match.group(1).strip()
                prereq_ranks = int(match.group(2))
                prerequisites.append({"talent": prereq_name, "ranks": prereq_ranks})
            
            # Derived field: points_in_tree_required
            # Based on standard Classic+ talent tree progression:
            # Tier 1: 0 points (character level 10)
            # Tier 2: 5 points (character level 15)
            # Tier 3: 10 points (character level 20)
            # Tier 4: 15 points (character level 25)
            # Tier 5: 20 points (character level 30)
            # Tier 6: 25 points (character level 35)
            # Tier 7: 30 points (character level 40)
            points_in_tree_required = (talent_tier - 1) * 5 if talent_tier > 0 else 0


            talents_in_tree[name] = {
                "level": level_req,
                "max_rank": max_rank,
                "tier": talent_tier,
                "prerequisites": prerequisites,
                "points_in_tree_required": points_in_tree_required
            }
        
        final_structured_talents[class_name][current_tree_name] = talents_in_tree

    print(json.dumps(final_structured_talents[class_name], indent=2))
    return final_structured_talents[class_name]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python extract_talents.py <html_file_path> <class_name>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    class_name = sys.argv[2]
    extract_talents_with_structure(html_file, class_name)
