#!/usr/bin/env python3
"""
Generate the main index pages and section index pages for the Hugo blog:
  - content/_index.md    (Português do Brasil)
  - content/<section>/_index.md    (Português do Brasil, per section)

Scans all markdown files in content/, extracts frontmatter metadata,
groups posts by year/month, and generates a chronological listing
with the most recent posts first.

Usage:
    scripts/generate_index.py

Script original by thyagobrejao and modified
"""

import os
import re
import sys
from datetime import datetime, timezone
from collections import defaultdict

# Project root is one level up from the scripts directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
INDEX_FILE_PT = os.path.join(CONTENT_DIR, "_index.md")
INDEX_FILE_EN = os.path.join(CONTENT_DIR, "_index.en.md")

# Files and directories to skip
SKIP_FILES = {"_index.md", "_index.en.md", "about.md", "about.en.md"}
SKIP_DIRS = {".git", "public", "themes", "static", "assets"}

MONTH_NAMES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

MONTH_NAMES_EN = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
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

    tags_match = re.search(
        r"tags:\s*\n((?:\s*-\s*.+\n?)+)", frontmatter_text
    )
    if tags_match:
        tags = re.findall(r"-\s*(.+)", tags_match.group(1))
        data["tags"] = [t.strip().strip("'\"") for t in tags]

    return data


def parse_date(date_str):
    """Parse a date string from frontmatter into a datetime object."""
    if not date_str:
        return None

    # Try ISO 8601 with timezone
    for fmt in [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(date_str.replace("'", "").replace('"', ""), fmt)
        except ValueError:
            continue

    # Handle timezone offset like -03:00
    cleaned = re.sub(r"([+-]\d{2}):(\d{2})$", r"\1\2", date_str)
    try:
        return datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None


def get_en_filepath(filepath):
    """Get the English translation filepath for a given pt-br file."""
    base, ext = os.path.splitext(filepath)
    return base + ".en" + ext


def get_section(filepath):
    """Get the top-level section name for a post (e.g. 'projetos', 'tecnologias').
    Returns None if the post is directly in the content root."""
    rel_path = os.path.relpath(filepath, CONTENT_DIR)
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        return parts[0]
    return None


def collect_posts():
    """Walk the content directory and collect all post metadata (pt-br and en)."""
    posts_pt = []
    posts_en = []

    for root, dirs, files in os.walk(CONTENT_DIR):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if not filename.endswith(".md"):
                continue
            if filename in SKIP_FILES:
                continue
            # Skip English translations (processed alongside pt-br)
            if filename.endswith(".en.md"):
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

            title_pt = frontmatter.get("title", os.path.splitext(filename)[0])
            date = parse_date(frontmatter.get("date", ""))
            tags_pt = frontmatter.get("tags", [])

            # Skip future posts
            if date:
                now_cmp = datetime.now(date.tzinfo) if date.tzinfo else datetime.now()
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

            posts_pt.append({
                "title": title_pt,
                "date": date,
                "tags": tags_pt,
                "url": url,
                "section": section,
            })

            # Try to get English translation
            en_filepath = get_en_filepath(filepath)
            title_en = title_pt  # fallback to pt-br title
            tags_en = tags_pt    # fallback to pt-br tags
            if os.path.exists(en_filepath):
                en_frontmatter = parse_frontmatter(en_filepath)
                if en_frontmatter:
                    title_en = en_frontmatter.get("title", title_pt)
                    tags_en = en_frontmatter.get("tags", tags_pt)

            posts_en.append({
                "title": title_en,
                "date": date,
                "tags": tags_en,
                "url": url,
                "section": section,
            })

    # Sort by date, most recent first
    posts_pt.sort(key=lambda p: p["date"] or datetime.min, reverse=True)
    posts_en.sort(key=lambda p: p["date"] or datetime.min, reverse=True)
    return posts_pt, posts_en


def generate_index(posts, lang="pt", title=None):
    """Generate the _index.md content with posts grouped by year/month."""
    lines = []

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if lang == "en":
        month_names = MONTH_NAMES_EN
        default_title = "Blog Thyago.dev.br"
        header = "## Latest Posts"
        empty_msg = "No published posts yet. Stay tuned!"
        no_date = "### No date"
        date_fmt = "%m/%d/%Y"
    else:
        month_names = MONTH_NAMES_PT
        default_title = "Blog Thyago.dev.br"
        header = "## Últimos Posts"
        empty_msg = "Nenhum post publicado ainda. Em breve teremos novidades!"
        no_date = "### Sem data"
        date_fmt = "%d/%m/%Y"

    display_title = title or default_title

    # Frontmatter
    lines.append("---")
    lines.append(f"date: '{now}'")
    lines.append("draft: false")
    lines.append(f"title: '{display_title}'")
    lines.append("cascade:")
    lines.append("  type: docs")
    lines.append("---")
    lines.append("")
    lines.append(header)
    lines.append("")

    if not posts:
        lines.append(empty_msg)
        return "\n".join(lines) + "\n"

    # Group by year/month
    grouped = defaultdict(list)
    for post in posts:
        if post["date"]:
            key = (post["date"].year, post["date"].month)
        else:
            key = (0, 0)
        grouped[key].append(post)

    # Sort keys by date descending
    sorted_keys = sorted(grouped.keys(), reverse=True)

    for year, month in sorted_keys:
        if year == 0:
            lines.append(no_date)
        else:
            month_name = month_names.get(month, "")
            lines.append(f"### {month_name} {year}")
        lines.append("")

        for post in grouped[(year, month)]:
            date_str = ""
            if post["date"]:
                date_str = post["date"].strftime(date_fmt)

            tag_str = ""
            if post["tags"]:
                tag_str = " — " + ", ".join(f"`{t}`" for t in post["tags"])

            lines.append(f"- [{post['title']}]({post['url']}) *({date_str})*{tag_str}")

        lines.append("")

    return "\n".join(lines) + "\n"


def get_section_frontmatter(section_dir, lang):
    """Read existing section _index frontmatter to preserve title and tags."""
    if lang == "en":
        index_file = os.path.join(section_dir, "_index.en.md")
    else:
        index_file = os.path.join(section_dir, "_index.md")

    if os.path.exists(index_file):
        fm = parse_frontmatter(index_file)
        if fm:
            return fm.get("title"), fm.get("tags", [])
    return None, []


def get_sections_with_posts(posts):
    """Get the set of section names that have at least one published post."""
    sections = set()
    for post in posts:
        if post.get("section"):
            sections.add(post["section"])
    return sections


def filter_posts_by_section(posts, section):
    """Filter posts to only include those in the given section."""
    return [p for p in posts if p.get("section") == section]


def generate_section_index(posts, lang, title, tags):
    """Generate a section _index.md content with posts grouped by year/month."""
    lines = []

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if lang == "en":
        month_names = MONTH_NAMES_EN
        header = "## Latest Posts"
        no_date = "### No date"
        date_fmt = "%m/%d/%Y"
    else:
        month_names = MONTH_NAMES_PT
        header = "## Últimos Posts"
        no_date = "### Sem data"
        date_fmt = "%d/%m/%Y"

    # Frontmatter
    lines.append("---")
    lines.append(f"title: \"{title}\"")
    lines.append(f"date: '{now}'")
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
    lines.append("draft: false")
    lines.append("---")
    lines.append("")
    lines.append(header)
    lines.append("")

    if not posts:
        if lang == "en":
            lines.append("No published posts yet. Stay tuned!")
        else:
            lines.append("Nenhum post publicado ainda. Em breve teremos novidades!")
        return "\n".join(lines) + "\n"

    # Group by year/month
    grouped = defaultdict(list)
    for post in posts:
        if post["date"]:
            key = (post["date"].year, post["date"].month)
        else:
            key = (0, 0)
        grouped[key].append(post)

    sorted_keys = sorted(grouped.keys(), reverse=True)

    for year, month in sorted_keys:
        if year == 0:
            lines.append(no_date)
        else:
            month_name = month_names.get(month, "")
            lines.append(f"### {month_name} {year}")
        lines.append("")

        for post in grouped[(year, month)]:
            date_str = ""
            if post["date"]:
                date_str = post["date"].strftime(date_fmt)

            tag_str = ""
            if post["tags"]:
                tag_str = " — " + ", ".join(f"`{t}`" for t in post["tags"])

            lines.append(f"- [{post['title']}]({post['url']}) *({date_str})*{tag_str}")

        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    print("Scanning content directory...")
    posts_pt, posts_en = collect_posts()
    print(f"Found {len(posts_pt)} published post(s)")

    # Generate section-level indices (blog, docs, projects, etc.)
    sections = get_sections_with_posts(posts_pt)
    for section in sorted(sections):
        section_dir = os.path.join(CONTENT_DIR, section)
        if not os.path.isdir(section_dir):
            continue

        section_posts_pt = filter_posts_by_section(posts_pt, section)
        section_posts_en = filter_posts_by_section(posts_en, section)

        # Get existing frontmatter titles/tags
        title_pt, tags_pt = get_section_frontmatter(section_dir, "pt")
        title_en, tags_en = get_section_frontmatter(section_dir, "en")

        # Fallback titles
        if not title_pt:
            title_pt = section.replace("-", " ").title()
        if not title_en:
            title_en = section.replace("-", " ").title()

        # Generate pt-br section index
        section_index_pt = os.path.join(section_dir, "_index.md")
        content = generate_section_index(section_posts_pt, "pt", title_pt, tags_pt)
        with open(section_index_pt, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Section index generated (pt-br): {section_index_pt}")

        # Generate en section index
        # section_index_en = os.path.join(section_dir, "_index.en.md")
        # content = generate_section_index(section_posts_en, "en", title_en, tags_en)
        # with open(section_index_en, "w", encoding="utf-8") as f:
        #    f.write(content)
        # print(f"Section index generated (en): {section_index_en}")


if __name__ == "__main__":
    main()