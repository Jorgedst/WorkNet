import os
import re

VIEWS_DIR = r"c:\Users\Dsilv\Downloads\WorkNet\views"
FILES = [
    "companies_view.py",
    "dashboard_view.py",
    "jobs_view.py",
    "network_view.py",
    "profile_view.py",
    "projects_view.py"
]

for file in FILES:
    filepath = os.path.join(VIEWS_DIR, file)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Add time.sleep(0.05) to _load_data
    if "import time" not in content and "def _load_data():" in content:
        content = content.replace("def _load_data():", "import time\n    def _load_data():\n        time.sleep(0.05)")
    elif "def _load_data():\n        try:" in content:
        content = content.replace("def _load_data():\n        try:", "def _load_data():\n        import time\n        time.sleep(0.05)\n        try:")

    # Replace threading.Thread(...) with page.run_thread
    # Because of previous changes, some might have threading.Thread and some page.run_thread
    content = re.sub(r"threading\.Thread\(target=_load_data, daemon=True\)\.start\(\)", "page.run_thread(_load_data)", content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file}")
