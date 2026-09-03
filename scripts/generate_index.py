#!/usr/bin/env python3
"""
Generate the main index page for the Hugo blog:
  - content/_index.md    (Português do Brasil)

Scans all markdown files in content/, extracts frontmatter metadata,
groups posts by year/month, and generates a chronological listing
with the most recent posts first.

Script original by thyagobrejao and modified
"""

import os
import re
from datetime import datetime, timezone
from collections import defaultdict

# Project root is one level up from the scripts directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
INDEX_FILE = os.path.join(CONTENT_DIR, "_index.md") # main index

# Files and directories to skip
SKIP_FILES = {"_index.md", "about.md"}
SKIP_DIRS = {".git", "public", "themes", "static", "assets"}

MONTH_NAMES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def parse_frontmatter(filepath):
    """Extract frontmatter fields from a markdown file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, UnicodeDecodeError):
        return None

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    data = {}

    # Parse simple YAML key-value pairs
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("-"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            data[key] = value

    # Parse tags: support inline array format ["tag1", "tag2"] or block list - tag
    if "tags" in data and isinstance(data["tags"], str):
        val = data["tags"].strip()
        if val.startswith("[") and val.endswith("]"):
            items = re.findall(r'[^,\[\]"\'\s]+', val)
            data["tags"] = [i.strip() for i in items if i.strip()]
        elif val:
            data["tags"] = [val]
        else:
            data["tags"] = []

    tags_match = re.search(r"tags:\s*\n((?:\s*-\s*.+\n?)+)", frontmatter_text)
    if tags_match:
        tags = re.findall(r"-\s*(.+)", tags_match.group(1))
        data["tags"] = [t.strip().strip("'\"") for t in tags]

    return data


def parse_date(date_str):
    """Parse a date string from frontmatter into a timezone-aware datetime object."""
    if not date_str:
        return None

    date_str_clean = date_str.replace("'", "").replace('"', "")

    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    # Handle timezone offset like -03:00
    cleaned = re.sub(r"([+-]\d{2}):(\d{2})$", r"\1\2", date_str_clean)
    try:
        dt = datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S%z")
        return dt
    except ValueError:
        return None

def collect_posts():
    """Walk the content directory and collect all post metadata."""
    posts = []

    for root, dirs, files in os.walk(CONTENT_DIR):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if not filename.endswith(".md") or filename in SKIP_FILES:
                continue

            filepath = os.path.join(root, filename)
            frontmatter = parse_frontmatter(filepath)
            if not frontmatter:
                continue

            # Skip drafts
            if frontmatter.get("draft", "false").lower() == "true":
                continue

            # Skip coming soon pages
            if frontmatter.get("coming_soon", "false").lower() == "true":
                continue

            title = frontmatter.get("title", os.path.splitext(filename)[0])
            date = parse_date(frontmatter.get("date", ""))
            tags = frontmatter.get("tags", [])

            if date:
                now_cmp = datetime.now(timezone.utc)
                if date > now_cmp:
                    continue

            # Calculate relative path from content dir for the link
            rel_path = os.path.relpath(filepath, CONTENT_DIR)
            # Convert file path to Hugo URL path
            url_path = os.path.splitext(rel_path)[0]
            # Handle index files
            if url_path.endswith("/index"):
                url_path = url_path[:-6]
            # Handle _index files (section pages)
            if url_path.endswith("/_index") or url_path == "_index":
                continue

            url = "/" + url_path.replace(os.sep, "/") + "/"

            posts.append({
                "title": title,
                "date": date,
                "tags": tags,
                "url": url,
            })

    min_datetime = datetime.min.replace(tzinfo=timezone.utc)
    posts.sort(key=lambda p: p["date"] or min_datetime, reverse=True)
    return posts


def generate_index(posts, title=None):
    """Generate the root _index.md content."""
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    display_title = title or "Blog"

    lines.extend([
        "---",
        f"date: '{now}'",
        "draft: false",
        "cascade:",
        "  type: ",
        "---",
        "",
        "{{< cards >}}",
        "{{< card link=\"blog\" title=\"Blog\" icon=\"newspaper\" >}}",
        "{{< card link=\"docs\" title=\"Documentação\" icon=\"book-open\" >}}",
        "{{< card link=\"about\" title=\"Sobre\" icon=\"user\" >}}",
        "{{< card link=\"projects\" title=\"Projetos\" icon=\"folder\" >}}",
        "{{< /cards >}}",
        "## Últimos Posts",
        ""
    ])

    if not posts:
        lines.append("Nenhum post publicado ainda")
        return "\n".join(lines) + "\n"

    grouped = defaultdict(list)
    for post in posts:
        key = (post["date"].year, post["date"].month) if post["date"] else (0, 0)
        grouped[key].append(post)

    for year, month in sorted(grouped.keys(), reverse=True):
        if year == 0:
            lines.append("### Sem data")
        else:
            lines.append(f"### {MONTH_NAMES_PT.get(month, '')} {year}")
        lines.append("")

        for post in grouped[(year, month)]:
            date_str = post["date"].strftime("%d/%m/%Y") if post["date"] else ""
            tag_str = " — " + ", ".join(f"`{t}`" for t in post["tags"]) if post["tags"] else ""
            lines.append(f"- [{post['title']}]({post['url']}) *({date_str})*{tag_str}")

        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    print("Scanning content directory...")
    posts = collect_posts()
    print(f"Found {len(posts)} published post(s)")

    # Generate root _index.md
    root_content = generate_index(posts)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(root_content)
    print(f"Main index generated: {INDEX_FILE}")


if __name__ == "__main__":
    main()