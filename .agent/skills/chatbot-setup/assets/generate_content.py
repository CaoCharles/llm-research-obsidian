"""
MkDocs Hook: 在 build 完成後自動生成 content.json
複製此檔案到專案的 hooks/ 目錄
"""

import json
import re
from pathlib import Path


def _fix_md_links(text, site_url, current_file_dir):
    """
    將 markdown 內容中的 .md 相對連結轉換為正確的網站 URL。
    例如: [紅隊演練](../Security-RedTeam/red-teaming-guide.md)
       -> [紅隊演練](https://site/Security-RedTeam/red-teaming-guide/)
    """
    def replace_link(match):
        link_text = match.group(1)
        url = match.group(2)

        # 跳過已經是完整 URL、錨點、或非 .md 連結
        if url.startswith(('http://', 'https://', '#', 'mailto:')):
            return match.group(0)

        # 處理 .md 連結（可能帶有錨點如 file.md#section）
        if '.md' in url:
            # 分離錨點
            anchor = ''
            if '#' in url:
                url, anchor = url.split('#', 1)
                anchor = '#' + anchor

            # 解析相對路徑
            resolved = (current_file_dir / url).resolve()
            try:
                rel_to_docs = resolved.relative_to(Path.cwd())
                # 轉換為 URL 路徑
                url_path = str(rel_to_docs).replace('\\', '/')
                # 移除 docs/ 前綴
                if url_path.startswith('docs/'):
                    url_path = url_path[5:]
                # .md -> /
                url_path = url_path.replace('.md', '/')
                # index/ -> 上層目錄
                if url_path.endswith('index/'):
                    url_path = url_path[:-6]

                full_url = f"{site_url}/{url_path}{anchor}"
                # 清理雙斜線
                full_url = full_url.replace('//', '/').replace('https:/', 'https://')
                return f"[{link_text}]({full_url})"
            except ValueError:
                pass

        return match.group(0)

    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)


def _strip_frontmatter(text):
    """移除 YAML frontmatter，減少 content.json 大小"""
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            return text[end + 3:].lstrip('\n')
    return text


def on_post_build(config, **kwargs):
    """
    在 MkDocs build 完成後執行
    生成 content.json 供 chatbot 使用
    """

    site_dir = Path(config['site_dir'])
    docs_dir = Path(config['docs_dir'])

    print("=" * 50)
    print("Generating content.json...")

    site_url = config.get('site_url', '').rstrip('/')
    content = []

    for md_file in sorted(docs_dir.rglob('*.md')):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                text = f.read()

            rel_path = md_file.relative_to(docs_dir)
            url_path = '/' + str(rel_path).replace('\\', '/').replace('.md', '/')

            if url_path.endswith('index/'):
                url_path = url_path[:-6]
            if url_path == '/index/':
                url_path = '/'

            full_url = site_url + url_path

            # 提取標題
            title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
            lines = text.split('\n')
            for line in lines:
                if line.strip().startswith('# '):
                    title = line.strip()[2:].strip()
                    break

            # 處理內容：移除 frontmatter + 修正 .md 連結
            cleaned_text = _strip_frontmatter(text)
            cleaned_text = _fix_md_links(cleaned_text, site_url, md_file.parent)

            content.append({
                'title': title,
                'url': full_url,
                'content': cleaned_text
            })

            print(f"  [OK] {md_file.name} -> {full_url}")

        except Exception as e:
            print(f"  [ERROR] {md_file}: {e}")

    output_file = site_dir / 'content.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"[SUCCESS] Generated {output_file}")
    print(f"[SUCCESS] Processed {len(content)} pages")
