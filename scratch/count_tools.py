
import re
import os

def count_tools(file_path):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all name: "something" in toolDefinitions
        # In the compiled code, it might be name:"something" or name: "something"
        matches = re.findall(r'name:\s*["\'](\w+)["\']', content)
        return len(matches)

path = r'C:\Users\victor.bernardi\.gemini\antigravity\extensions\google-drive-mcp\node_modules\@piotr-agier\google-drive-mcp\dist\index.js'
print(f"Google Drive Tools: {count_tools(path)}")
