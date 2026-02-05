#!/usr/bin/env python3
"""Fix topic pages to remove [tag] and show full paper titles."""
import re
import os
from pathlib import Path

topics_dir = Path("docs/Topics")

for md_file in topics_dir.glob("*.md"):
    content = md_file.read_text(encoding='utf-8')
    
    # Pattern: - `[tag]` [[[arxiv_id] Full Title|Short Title...]] (date)
    pattern = r"- `\[([^\]]+)\]` \[\[\[(\d+\.\d+)\] ([^\|]+)\|([^\]]+)\]\] \((\d{4}-\d{2}-\d{2})\)"
    
    def replace_paper_link(match):
        arxiv_id = match.group(2)
        full_title = match.group(3).strip()
        date = match.group(5)
        # Use simpler relative path
        link_path = f"../Papers/[{arxiv_id}] {full_title}.md"
        return f"- [{full_title}]({link_path}) ({date})"
    
    new_content = re.sub(pattern, replace_paper_link, content)
    
    if new_content != content:
        md_file.write_text(new_content, encoding='utf-8')
        print(f"Updated: {md_file.name}")

print("Done!")
