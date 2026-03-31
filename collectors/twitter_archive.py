#!/usr/bin/env python3
"""
Parse a Twitter/X data export into structured markdown.
Download your archive: Settings → Your Account → Download an archive of your data.

Usage:
    python twitter_archive.py ~/Downloads/twitter-2024-01-01/ -o _raw/social/

Output:
    _raw/social/tweets.md          — original tweets
    _raw/social/replies.md         — replies (high persona signal)
    _raw/social/quotes.md          — quote tweets
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_tweets(archive_dir: str) -> list[dict]:
    """Load tweets from Twitter archive format."""
    tweets_path = Path(archive_dir) / "data" / "tweets.js"

    if not tweets_path.exists():
        # Try alternative path
        tweets_path = Path(archive_dir) / "data" / "tweet.js"

    if not tweets_path.exists():
        print(f"Cannot find tweets.js in {archive_dir}/data/", file=sys.stderr)
        print("Expected Twitter archive structure: archive/data/tweets.js", file=sys.stderr)
        sys.exit(1)

    content = tweets_path.read_text(encoding="utf-8")

    # Twitter archive JS files start with "window.YTD.tweets.part0 = "
    # Remove the JS variable assignment to get valid JSON
    eq_pos = content.find("= ")
    if eq_pos != -1:
        content = content[eq_pos + 2:]

    data = json.loads(content)

    tweets = []
    for item in data:
        tweet = item.get("tweet", item)
        tweets.append({
            "id": tweet.get("id_str", tweet.get("id", "")),
            "text": tweet.get("full_text", tweet.get("text", "")),
            "created_at": tweet.get("created_at", ""),
            "in_reply_to": tweet.get("in_reply_to_screen_name"),
            "is_retweet": tweet.get("full_text", "").startswith("RT @"),
            "quote_url": None,
        })

        # Check for quote tweet
        entities = tweet.get("entities", {})
        urls = entities.get("urls", [])
        for url in urls:
            expanded = url.get("expanded_url", "")
            if "twitter.com/" in expanded and "/status/" in expanded:
                tweets[-1]["quote_url"] = expanded

    return tweets


def parse_date(date_str: str) -> str:
    """Parse Twitter date format to ISO date."""
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "unknown"


def classify_tweets(tweets: list[dict]) -> dict[str, list[dict]]:
    original = []
    replies = []
    quotes = []

    for t in tweets:
        if t["is_retweet"]:
            continue  # Skip pure retweets — no persona signal
        if t["in_reply_to"]:
            replies.append(t)
        elif t["quote_url"]:
            quotes.append(t)
        else:
            original.append(t)

    return {"tweets": original, "replies": replies, "quotes": quotes}


def tweets_to_markdown(tweets: list[dict], category: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        "source_type: tweet",
        f"category: {category}",
        f"count: {len(tweets)}",
        f"collected_at: {now}",
        "---",
        "",
        f"# {category.title()} ({len(tweets)})",
        "",
    ]

    # Sort by date, newest first
    sorted_tweets = sorted(tweets, key=lambda t: t["created_at"], reverse=True)

    for t in sorted_tweets:
        date = parse_date(t["created_at"])
        text = t["text"].strip()

        lines.append(f"## {date}")
        if category == "replies" and t["in_reply_to"]:
            lines.append(f"> Replying to @{t['in_reply_to']}")
            lines.append("")
        lines.append(text)
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parse Twitter archive to markdown")
    parser.add_argument("archive_dir", help="Path to extracted Twitter archive directory")
    parser.add_argument("-o", "--output", default="_raw/social", help="Output directory")
    args = parser.parse_args()

    tweets = load_tweets(args.archive_dir)
    print(f"Loaded {len(tweets)} items from archive")

    classified = classify_tweets(tweets)
    os.makedirs(args.output, exist_ok=True)

    for category, items in classified.items():
        if not items:
            continue
        content = tweets_to_markdown(items, category)
        filepath = os.path.join(args.output, f"{category}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {filepath} ({len(items)} {category})")

    total = sum(len(v) for v in classified.values())
    skipped = len(tweets) - total
    print(f"\nDone. {total} tweets saved, {skipped} pure retweets skipped.")


if __name__ == "__main__":
    main()
