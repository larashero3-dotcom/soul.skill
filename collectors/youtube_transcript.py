#!/usr/bin/env python3
"""
Extract YouTube video transcripts as markdown.
Uses youtube-transcript-api (no API key needed).

Usage:
    python youtube_transcript.py "https://youtube.com/watch?v=xxxxx" -o _raw/interviews/
    python youtube_transcript.py --batch video_urls.txt -o _raw/interviews/

Install:
    pip install youtube-transcript-api
"""

import argparse
import os
import re
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")
    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/embed/") or parsed.path.startswith("/v/"):
            return parsed.path.split("/")[2]
    return None


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_]+", "-", text).strip("-")
    return text[:max_len]


def format_timestamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_transcript(video_id: str, langs: list[str] | None = None) -> list[dict]:
    if langs is None:
        langs = ["zh-Hans", "zh", "en", "zh-Hant", "ja", "ko"]

    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=langs)
    return [
        {"text": entry.text, "start": entry.start, "duration": entry.duration}
        for entry in transcript
    ]


def transcript_to_markdown(entries: list[dict], with_timestamps: bool = True) -> str:
    lines = []
    for entry in entries:
        text = entry["text"].strip()
        if not text:
            continue
        if with_timestamps:
            ts = format_timestamp(entry["start"])
            lines.append(f"**[{ts}]** {text}")
        else:
            lines.append(text)

    if with_timestamps:
        return "\n\n".join(lines)
    else:
        return " ".join(lines)


def process_video(url: str, output_dir: str, with_timestamps: bool) -> None:
    video_id = extract_video_id(url)
    if not video_id:
        print(f"  ✗ Cannot parse video ID from: {url}", file=sys.stderr)
        return

    try:
        entries = fetch_transcript(video_id)
    except Exception as e:
        print(f"  ✗ {url} — {e}", file=sys.stderr)
        return

    content = transcript_to_markdown(entries, with_timestamps)

    os.makedirs(output_dir, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d")
    filename = f"{video_id}.md"
    filepath = os.path.join(output_dir, filename)

    frontmatter = f"""---
source_type: transcript
source_url: {url}
video_id: {video_id}
collected_at: {now}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(f"# Transcript: {video_id}\n\n")
        f.write(content)
        f.write("\n")

    print(f"  ✓ {filepath} ({len(entries)} segments)")


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube transcripts")
    parser.add_argument("url", nargs="?", help="YouTube video URL")
    parser.add_argument("--batch", help="File containing video URLs (one per line)")
    parser.add_argument("-o", "--output", default="_raw/interviews", help="Output directory")
    parser.add_argument("--no-timestamps", action="store_true", help="Output plain text without timestamps")
    args = parser.parse_args()

    if not args.url and not args.batch:
        parser.error("Provide a URL or --batch file")

    urls = []
    if args.batch:
        with open(args.batch) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    if args.url:
        urls.append(args.url)

    print(f"Extracting transcripts for {len(urls)} video(s) → {args.output}/\n")

    for url in urls:
        process_video(url, args.output, not args.no_timestamps)

    print(f"\nDone. {len(urls)} video(s) processed.")


if __name__ == "__main__":
    main()
