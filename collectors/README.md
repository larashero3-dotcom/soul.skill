# Collectors

Lightweight scripts for gathering raw material before distillation. All scripts output markdown files to your `_raw/` directory.

## Requirements

```bash
pip install requests youtube-transcript-api
```

No API keys needed. No heavy dependencies.

## Scripts

### `fetch_url.py` — Any URL → Markdown

Converts a web page (blog post, article, newsletter) into clean markdown using the [Jina Reader API](https://jina.ai/reader/) (free, no auth required).

```bash
# Single URL
python collectors/fetch_url.py "https://example.com/article" -o _raw/writing/

# Multiple URLs from a file (one URL per line)
python collectors/fetch_url.py --batch urls.txt -o _raw/writing/
```

Works with: blogs, Substack, Medium, most news sites, some WeChat articles.

### `youtube_transcript.py` — YouTube → Transcript

Extracts subtitles/captions from YouTube videos. Supports auto-generated and manual captions in any language.

```bash
# Single video
python collectors/youtube_transcript.py "https://youtube.com/watch?v=xxxxx" -o _raw/interviews/

# Entire channel or playlist (provide video URLs in a file)
python collectors/youtube_transcript.py --batch video_urls.txt -o _raw/interviews/
```

### `twitter_archive.py` — Twitter/X 自助导出 → Markdown

**仅限自助导出场景**：解析你自己的 Twitter 官方数据导出包（Settings → Your Account → Download an archive of your data），提取推文、回复、引用推到结构化 markdown。

```bash
# 指向你解压后的 archive 目录
python collectors/twitter_archive.py ~/Downloads/twitter-archive/ -o _raw/social/
```

导出步骤：[Twitter → Settings → Your Account → Download an archive of your data](https://twitter.com/settings/download_your_data)，Twitter 需要 24-48 小时准备。

> **⚠️ 重要限制：这个脚本只能处理你自己账号的导出数据。**
>
> X/Twitter 的现状是：自动抓取他人推文几乎不可行——
> - **官方 API**：免费层级已基本不可用，付费 API（Basic $100/月起）才能批量读取，违反本工具集"零 API key"原则
> - **爬虫 / 第三方工具**：X 反爬极其激进（频繁改版、IP 封禁、登录墙），不稳定且违反 ToS
>
> **如果目标人物不配合提供自己的导出包，推特数据基本拿不到。** 建议用其他来源补偿：
> - **即刻**：用 `jike_export.py` 采集，很多中文圈 KOL 在即刻更活跃
> - **博客 / Newsletter**：用 `fetch_url.py` 批量抓取
> - **播客 / YouTube**：用 `youtube_transcript.py` 拿逐字稿，人格信号往往比推文更丰富

### `jike_export.py` — 即刻 (Jike) Posts → Markdown

Extracts posts from a 即刻 user profile. Requires the user's profile URL.

```bash
python collectors/jike_export.py "https://web.okjike.com/u/xxxxx" -o _raw/social/
```

> Note: 即刻 has no official API. This script uses the web interface and may break if 即刻 changes their site. For reliability, consider manually exporting via the 即刻 app's "我的动态" feature.

## What These Scripts Don't Cover

Some sources require heavier tools or manual work:

| Source | Recommended Approach |
|--------|---------------------|
| **Podcasts / audio** | Download audio with [yt-dlp](https://github.com/yt-dlp/yt-dlp), transcribe with [Whisper](https://github.com/openai/whisper) or [Deepgram](https://deepgram.com). Speaker diarization: [pyannote](https://github.com/pyannote/pyannote-audio). |
| **WeChat articles (公众号)** | Try `fetch_url.py` first — it works for some. If blocked, manually copy-paste or use [WeChatDownload](https://github.com/AntoineDly/WeChatDownload). |
| **Weibo** | No reliable open tool. Manual export or browser automation. |
| **Chat logs (WeChat/Slack/Discord)** | Export from the platform (Slack: workspace export; Discord: [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter); WeChat: backup tools). Always get permission first. |
| **Books / PDFs** | [PyMuPDF](https://pymupdf.readthedocs.io/) or [pdfplumber](https://github.com/jsvine/pdfplumber) for text extraction. |

## Output Format

All scripts output markdown files with a consistent frontmatter:

```yaml
---
source_type: tweet | article | transcript | post
source_url: https://...
author: Person Name
date: 2025-01-15
collected_at: 2026-03-30
---
```

This makes it easy for the distillation pipeline to process the corpus.

## Tips

- **More is better.** Don't pre-filter — collect everything and let the distillation pipeline sort it out.
- **Preserve metadata.** Dates matter for tracking belief evolution. URLs matter for source attribution.
- **Prioritize interviews and casual content.** Polished articles show how someone writes; podcasts and social posts show how someone thinks.
