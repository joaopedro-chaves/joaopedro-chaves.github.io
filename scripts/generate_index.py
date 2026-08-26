#!/usr/bin/env python3
"""
Generate the main index pages and section index pages for the Hugo blog:
  - content/_index.md    (Português do Brasil)
  - content/<section>/_index.md    (Português do Brasil, per section)

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
# DOCS_DIR = os.path.join(CONTENT_DIR, "docs") # local documents
# BLOG_DIR = os.path.join(CONTENT_DIR, "blog") # posts
# PROJECTS_DIR = os.path.join(CONTENT_DIR, "projects") # projects
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

def get_section(filepath):
    """Get the top-level section name for a post."""
    rel_path = os.path.relpath(filepath, CONTENT_DIR)
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        return parts[0]
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
            section = get_section(filepath)

            posts.append({
                "title": title,
                "date": date,
                "tags": tags,
                "url": url,
                "section": section,
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


def get_section_frontmatter(section_dir):
    """Read existing section _index frontmatter to preserve title and tags."""
    index_file = os.path.join(section_dir, "_index.md")

    if os.path.exists(index_file):
        fm = parse_frontmatter(index_file)
        if fm:
            return fm.get("title"), fm.get("tags", [])
    return None, []


def get_sections_with_posts(posts):
    """Get the set of section names that have at least one published post."""
    return {post["section"] for post in posts if post.get("section")}


def filter_posts_by_section(posts, section):
    """Filter posts to only include those in the given section."""
    return [p for p in posts if p.get("section") == section]

# generate _index.md for each section (not used, but useful for future)

# def generate_section_index(posts, title="", tags=None):
#    """Generate a section _index.md content."""
#    lines = []
#    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

#    lines.extend([
#        "---",
#        f'title: "{title}"',
#        f"date: '{now}'"
#    ])

#    if tags:
#        lines.append("tags:")
#        lines.extend([f"  - {tag}" for tag in tags])

#    lines.extend([
#        "draft: false",
#        "---",
#        "",
#        "## Últimos Posts",
#        ""
#    ])

#    if not posts:
#        lines.append("Nenhum post publicado ainda.")
#        return "\n".join(lines) + "\n"

#    # Group by year/month
#    grouped = defaultdict(list)
#    for post in posts:
#        key = (post["date"].year, post["date"].month) if post["date"] else (0, 0)
#        grouped[key].append(post)

#    for year, month in sorted(grouped.keys(), reverse=True):
#        if year == 0:
#            lines.append("### Sem data")
#        else:
#            lines.append(f"### {MONTH_NAMES_PT.get(month, '')} {year}")
#        lines.append("")

#        for post in grouped[(year, month)]:
#            date_str = post["date"].strftime("%d/%m/%Y") if post["date"] else ""
#            tag_str = " — " + ", ".join(f"`{t}`" for t in post["tags"]) if post["tags"] else ""
#            lines.append(f"- [{post['title']}]({post['url']}) *({date_str})*{tag_str}")

#        lines.append("")

#    return "\n".join(lines) + "\n"


def main():
    print("Scanning content directory...")
    posts = collect_posts()
    print(f"Found {len(posts)} published post(s)")

    # Generate root _index.md
    root_content = generate_index(posts)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(root_content)
    print(f"Main index generated: {INDEX_FILE}")

    # Generate section-level indices (blog, docs, etc.)
    sections = get_sections_with_posts(posts)
    for section in sorted(sections):
        section_dir = os.path.join(CONTENT_DIR, section)
        if not os.path.isdir(section_dir):
            continue

        section_posts = filter_posts_by_section(posts, section)

        # Get existing frontmatter titles/tags
        title, tags = get_section_frontmatter(section_dir)

        # Fallback titles
        if not title:
            title = section.replace("-", " ").title()

        # Generate section index
        # section_index = os.path.join(section_dir, "_index.md")
        # content = generate_section_index(section_posts, title, tags)
        # with open(section_index, "w", encoding="utf-8") as f:
        #     f.write(content)
        # print(f"Section index generated: {section_index}")


if __name__ == "__main__":
    main()