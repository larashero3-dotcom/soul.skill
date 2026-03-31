#!/usr/bin/env python3
"""
Fetch any URL and convert to clean markdown using Jina Reader API.
No API key required. Free tier: 20 RPM.

Usage:
    python fetch_url.py "https://example.com/article" -o _raw/writing/
    python fetch_url.py --batch urls.txt -o _raw/writing/
"""

import argparse
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

JINA_READER_PREFIX = "https://r.jina.ai/"
HEADERS = {
    "Accept": "text/markdown",
    "User-Agent": "soul.skill-collector/1.0",
}


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len]


def fetch_as_markdown(url: str) -> tuple[str, str]:
    """Returns (title, markdown_content)."""
    resp = requests.get(
        f"{JINA_READER_PREFIX}{url}",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()

    content = resp.text
    # Jina returns title as first line: "Title: ..."
    title = ""
    lines = content.split("\n", 1)
    if lines[0].startswith("Title:"):
        title = lines[0].removeprefix("Title:").strip()
        content = lines[1] if len(lines) > 1 else ""

    return title, content.strip()


def save_article(url: str, title: str, content: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    slug = slugify(title) if title else slugify(urlparse(url).path)
    if not slug:
        slug = slugify(urlparse(url).netloc)
    filename = f"{slug}.md"
    filepath = os.path.join(output_dir, filename)

    # Avoid overwriting
    counter = 1
    while os.path.exists(filepath):
        filepath = os.path.join(output_dir, f"{slug}-{counter}.md")
        counter += 1

    now = datetime.now().strftime("%Y-%m-%d")
    frontmatter = f"""---
source_type: article
source_url: {url}
title: "{title}"
collected_at: {now}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        if title:
            f.write(f"# {title}\n\n")
        f.write(content)
        f.write("\n")

    return filepath


def process_url(url: str, output_dir: str) -> None:
    try:
        title, content = fetch_as_markdown(url)
        filepath = save_article(url, title, content, output_dir)
        print(f"  ✓ {filepath}")
    except requests.RequestException as e:
        print(f"  ✗ {url} — {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Fetch URLs as markdown")
    parser.add_argument("url", nargs="?", help="Single URL to fetch")
    parser.add_argument("--batch", help="File containing URLs (one per line)")
    parser.add_argument("-o", "--output", default="_raw/writing", help="Output directory")
    args = parser.parse_args()

    if not args.url and not args.batch:
        parser.error("Provide a URL or --batch file")

    urls = []
    if args.batch:
        with open(args.batch) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if args.url:
        urls.append(args.url)

    print(f"Fetching {len(urls)} URL(s) → {args.output}/\n")

    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(3)  # Respect Jina rate limit (20 RPM)
        process_url(url, args.output)

    print(f"\nDone. {len(urls)} URL(s) processed.")


if __name__ == "__main__":
    main()
