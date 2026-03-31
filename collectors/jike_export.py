#!/usr/bin/env python3
"""
Export 即刻 (Jike) user posts to markdown.
Uses the 即刻 web API (unofficial, may break).

Usage:
    python jike_export.py "https://web.okjike.com/u/xxxxxxxx" -o _raw/social/
    python jike_export.py --user-id "xxxxxxxx" -o _raw/social/

Note: 即刻 has no official API. This script may stop working if 即刻 changes
their web interface. For reliability, consider:
1. Using the 即刻 app's built-in export ("我的动态" → share)
2. Manually copying posts
3. Using browser automation as a fallback
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

API_BASE = "https://web-api.okjike.com/api/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://web.okjike.com/",
    "Origin": "https://web.okjike.com",
}


def extract_user_id(url_or_id: str) -> str:
    if url_or_id.startswith("http"):
        path = urlparse(url_or_id).path
        return path.rstrip("/").split("/")[-1]
    return url_or_id


def fetch_user_posts(user_id: str, max_pages: int = 20) -> list[dict]:
    """Fetch posts using 即刻 web GraphQL API."""
    posts = []
    load_more_key = None

    for page in range(max_pages):
        variables = {
            "username": user_id,
            "loadMoreKey": load_more_key,
        }
        payload = {
            "operationName": "UserProfile",
            "query": """
                query UserProfile($username: String!, $loadMoreKey: JSON) {
                    userProfile(username: $username) {
                        username
                        screenName
                    }
                    userPost(username: $username, loadMoreKey: $loadMoreKey) {
                        data {
                            id
                            content
                            createdAt
                            pictures { picUrl }
                            linkInfo { title linkUrl }
                        }
                        loadMoreKey
                    }
                }
            """,
            "variables": variables,
        }

        try:
            resp = requests.post(API_BASE, json=payload, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", {})
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"  ⚠ API request failed on page {page + 1}: {e}", file=sys.stderr)
            print("  即刻 web API may have changed. Consider manual export.", file=sys.stderr)
            break

        user_post = data.get("userPost", {})
        page_posts = user_post.get("data", [])

        if not page_posts:
            break

        screen_name = data.get("userProfile", {}).get("screenName", "")

        for post in page_posts:
            posts.append({
                "id": post.get("id", ""),
                "text": post.get("content", ""),
                "created_at": post.get("createdAt", ""),
                "author": screen_name,
                "has_images": bool(post.get("pictures")),
                "link_title": (post.get("linkInfo") or {}).get("title"),
                "link_url": (post.get("linkInfo") or {}).get("linkUrl"),
            })

        load_more_key = user_post.get("loadMoreKey")
        if not load_more_key:
            break

        print(f"  Page {page + 1}: {len(page_posts)} posts (total: {len(posts)})")
        time.sleep(1)  # Rate limiting

    return posts


def posts_to_markdown(posts: list[dict], user_id: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    author = posts[0]["author"] if posts else user_id

    lines = [
        "---",
        "source_type: post",
        "platform: jike",
        f"author: \"{author}\"",
        f"user_id: {user_id}",
        f"count: {len(posts)}",
        f"collected_at: {now}",
        "---",
        "",
        f"# {author} — 即刻动态 ({len(posts)} posts)",
        "",
    ]

    for post in posts:
        date = post["created_at"][:10] if post["created_at"] else "unknown"
        text = post["text"].strip()

        if not text:
            continue

        lines.append(f"## {date}")
        lines.append("")
        lines.append(text)

        if post["link_title"]:
            lines.append(f"\n> 🔗 [{post['link_title']}]({post['link_url']})")

        if post["has_images"]:
            lines.append("\n> 📷 [image attached]")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Export 即刻 user posts to markdown")
    parser.add_argument("url", nargs="?", help="即刻 profile URL (https://web.okjike.com/u/xxxxx)")
    parser.add_argument("--user-id", help="即刻 user ID directly")
    parser.add_argument("-o", "--output", default="_raw/social", help="Output directory")
    parser.add_argument("--max-pages", type=int, default=20, help="Max pages to fetch (default: 20)")
    args = parser.parse_args()

    if not args.url and not args.user_id:
        parser.error("Provide a 即刻 profile URL or --user-id")

    user_id = args.user_id or extract_user_id(args.url)
    print(f"Fetching posts for user: {user_id}\n")

    posts = fetch_user_posts(user_id, args.max_pages)

    if not posts:
        print("No posts found. The API may require authentication or the user ID may be incorrect.")
        print("\nFallback options:")
        print("1. Open the profile in browser and manually copy posts")
        print("2. Use the 即刻 app's share/export feature")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    content = posts_to_markdown(posts, user_id)
    filepath = os.path.join(args.output, f"jike-{user_id}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n  ✓ {filepath} ({len(posts)} posts)")
    print("Done.")


if __name__ == "__main__":
    main()
