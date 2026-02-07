from pathlib import Path
import re

def extract_next_task(prd_path: str|Path) -> str | None:
    """Extract the first unchecked task block from prd.md."""
    with open(prd_path, "r") as f:
        content = f.read()

    # Split into sections by major/sub-task headings
    sections = re.split(r'(^#{2,4}\s+.*$)', content, flags=re.MULTILINE)

    current_heading = None
    for part in sections:
        if re.match(r'^#{2,4}\s+', part):
            current_heading = part
        elif current_heading and '- [ ]' in part:
            # Found a section with unchecked boxes — return heading + body
            return current_heading + "\n" + part

    return None  # All done

def count_checked(prd_path: str) -> int:
    with open(prd_path, "r") as f:
        return len(re.findall(r'- \[x\]', f.read()))
