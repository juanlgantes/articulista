import os
import sys
from html.parser import HTMLParser

class LinkValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])

def get_project_root():
    # Assuming script is in <root>/verification/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)

def check_file_existence(filepath):
    if os.path.exists(filepath):
        print(f"[OK] File/Dir exists: {filepath}")
        return True
    else:
        print(f"[FAIL] Missing: {filepath}")
        return False

def verify_site():
    print("--- Starting Site Verification ---")
    
    root_dir = get_project_root()
    print(f"Project Root: {root_dir}")
    
    # 1. Check Required Structure
    required_paths = [
        "index.html",
        "css/style.css",
        "img",
        "js",
        "post-template.html"
    ]
    
    all_passed = True
    
    print("\n1. Checking File Structure:")
    for path in required_paths:
        full_path = os.path.join(root_dir, path)
        if not check_file_existence(full_path):
            all_passed = False

    # 2. Check Links in index.html
    print("\n2. Checking Links in index.html:")
    index_path = os.path.join(root_dir, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        parser = LinkValidator()
        parser.feed(content)
        
        for link in parser.links:
            # Ignore external links and anchors
            if link.startswith("http") or link.startswith("#"):
                continue
            
            # Simple check for relative paths
            full_link_path = os.path.join(root_dir, link)
            if not check_file_existence(full_link_path):
                print(f"  -> Broken link found in index.html: {link}")
                all_passed = False
                
    except Exception as e:
        print(f"[ERROR] Could not parse index.html: {e}")
        all_passed = False

    print("\n--- Verification Result ---")
    if all_passed:
        print("SUCCESS: All checks passed.")
        sys.exit(0)
    else:
        print("FAILURE: Issues found.")
        sys.exit(1)

if __name__ == "__main__":
    verify_site()
