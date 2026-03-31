# Persona Distillation Guide

A step-by-step pipeline for turning raw material about a person into a structured AI persona.

## Overview

```
Raw Material → Ingestion → 3-Pass Distillation → Structured Output → Skill
```

Total cost: ~$5–15 in API fees for a substantial corpus (10K tweets + 50 hours of interviews).

## Step 1: Collect Raw Material

Gather as much as possible. More input = better output. The table below lists every source type we've tested, with specific tools and tips for each.

### Source Types

#### Social Media Posts (High Value — reveals real voice)

| Platform | How to Collect | Tools | Tips |
|----------|---------------|-------|------|
| X / Twitter | Account data export (Settings → Your Account → Download Archive) or API | Twitter Archive, Tweepy, X API v2 | Export gives you ALL tweets including replies. Replies are often more revealing than main posts. |
| 即刻 (Jike) | Manual export or scraping | Browser automation, Jike API (unofficial) | 即刻动态 are gold — short, casual, authentic. Prioritize these for the "internal quotes" layer. |
| LinkedIn | Copy posts manually or use export | LinkedIn data export | Formal voice — good for "writing mode" calibration, less useful for casual personality. |
| 微博 (Weibo) | Weibo data export or scraping | Weibo API, browser automation | Filter out retweets without comment. |
| Reddit / forums | User profile scraping | Reddit API, Pushshift | Comments > posts for personality signal. |

**Target**: 200+ posts minimum. 500+ ideal.

#### Long-Form Writing (High Value — reveals thinking structure)

| Source | How to Collect | Tools | Tips |
|--------|---------------|-------|------|
| Blog / newsletter | Copy or scrape | Readability parsers, Jina Reader, Markdownify | Preserve the original structure (headings, lists) — it reveals how they organize thought. |
| WeChat articles (公众号) | URL extraction + conversion | WeChat article scrapers, browser automation | WeChat blocks most scraping — may need manual copy. Save full HTML for formatting signals. |
| Substack / Medium | RSS feed or direct scrape | RSS parser, Jina Reader | Substack has clean RSS. Medium needs auth bypass. |
| Internal docs (with permission) | Export from Notion / Google Docs / Confluence | Platform export tools | Internal docs are the highest-signal source — they show how someone thinks when not performing for an audience. **Always get explicit permission.** |

**Target**: 10+ articles / docs minimum. 30+ ideal.

#### Interviews & Podcasts (Very High Value — reveals spontaneous thinking)

| Source | How to Collect | Tools | Tips |
|--------|---------------|-------|------|
| Podcast episodes | Download audio → transcribe | yt-dlp (for podcast platforms), Whisper, Deepgram, AssemblyAI | **Speaker diarization is critical** — you need to know which words are theirs vs. the host's. Use Whisper large-v3 + pyannote for best results. |
| YouTube interviews | Subtitle extraction or audio download → transcribe | yt-dlp, YouTube Transcript API | YouTube auto-captions are ~90% accurate. Manual transcripts (if available) are better. |
| 小宇宙 (Xiaoyuzhou) podcasts | Audio download → transcribe | Browser automation, Whisper | Chinese podcast transcription: use Whisper large-v3 or FunASR for better Chinese accuracy. |
| Conference talks | YouTube / event platform → transcribe | yt-dlp, Whisper | Talks reveal their "presentation mode" — useful for the formal writing layer. |
| Media interviews (text) | Copy from publication | Web scraping | Text interviews often edit out the personality. Audio/video is always more authentic. |

**Target**: 3+ hours of audio minimum. 10+ hours ideal.

#### Books & Long Documents

| Source | How to Collect | Tools | Tips |
|--------|---------------|-------|------|
| Published books | PDF/EPUB → text extraction | PyMuPDF, Calibre, pdfplumber | Focus on passages where they express opinions, not where they cite data. |
| Slide decks | PDF/PPTX → text extraction | python-pptx, PyMuPDF | Slides show their information hierarchy — what they choose to emphasize first. |
| Email newsletters | Archive scrape or forward collection | - | Newsletter voice is often closest to their "real" writing voice. |

#### Chat Logs (Highest Authenticity — requires permission)

| Source | How to Collect | Tools | Tips |
|--------|---------------|-------|------|
| Slack | Workspace export (admin) or channel export | Slack Export | Filter to their messages only. Include thread replies — that's where personality lives. |
| Discord | Bot-based export | DiscordChatExporter | Same as Slack — threads > top-level messages. |
| WeChat / DM (with permission) | Manual screenshot → OCR, or chat record export | WeChat backup tools, OCR | The most authentic source. Even 50 messages can dramatically improve the casual mode. |
| Meeting transcripts | Zoom/Teams/Google Meet recording → transcribe | Platform transcription, Whisper | Meeting behavior (interrupting, questioning, summarizing) is a strong personality signal. |

**Important**: Always get explicit consent before using private communications.

### Corpus Quality Checklist

Before moving to distillation, verify your corpus covers these dimensions:

- [ ] **Casual voice** — at least 50 casual/chat-style data points
- [ ] **Formal voice** — at least 5 long-form pieces
- [ ] **Spontaneous thinking** — at least 1 hour of interview/podcast
- [ ] **Self-reflection** — at least a few instances of them admitting mistakes or uncertainty
- [ ] **Domain expertise** — enough material on their primary topics
- [ ] **Contradiction / evolution** — evidence of changing their mind on something

**Minimum viable corpus**: 50+ data points for a basic persona. 200+ for a convincing one. 500+ for near-indistinguishable.

### Raw Corpus Organization

Save all collected material in a `_raw/` directory:

```
_raw/
├── social/
│   ├── x-tweets-export.json
│   └── jike-posts.json
├── writing/
│   ├── blog-post-1.md
│   └── blog-post-2.md
├── interviews/
│   ├── podcast-ep42-transcript.md
│   └── youtube-interview-transcript.md
├── chat/
│   └── slack-messages.json
└── sources-index.md          # What you collected, from where, when
```

## Step 2: Distillation (3-Pass Pipeline)

### Pass 1: Chunk + Tag

Split all raw text into chunks (~2000 chars each). For each chunk, use AI to extract:

```yaml
topic: ["management", "product strategy"]
type: "opinion"          # opinion / fact / decision / emotion / casual
stance: "against micromanagement"
quote_worthy: true       # contains a memorable quote?
time_period: "2024-Q3"
```

**Prompt template:**

```
Analyze this text from {person_name}. Extract:
1. Main topics discussed (list of keywords)
2. Type of content: opinion, factual statement, decision, emotional expression, or casual chat
3. Their stance or position (one sentence)
4. Whether it contains a quote worth preserving (true/false)
5. Time period if identifiable

Text:
{chunk}
```

Use a fast, cheap model (Haiku / GPT-4o-mini) for this pass. It's classification, not generation.

### Pass 2: Cluster + Deduplicate + Rank

Group chunks by topic, then for each topic:

1. **Deduplicate**: Remove semantically similar chunks (keep the most articulate version)
2. **Rank**: Score by quote_worthy + engagement + recency
3. **Select**: Keep top 20–50 chunks per topic

```python
# Pseudocode
topics = group_by(all_chunks, key="topic")

for topic in topics:
    deduplicated = semantic_dedup(topic.chunks, threshold=0.85)
    ranked = rank(deduplicated, by=["quote_worthy", "engagement", "recency"])
    topic.selected = ranked[:50]
```

### Pass 3: Structured Writing

Feed selected chunks into a strong model (Opus / Sonnet / GPT-4) with specific prompts for each output document.

#### For `_persona/rules.md`:

```
You are a persona architect. Based on these raw materials from {person},
extract their personality into a structured persona document.

Required sections:
1. Identity (current role, background, public presence)
2. Core Personality (5-8 defining traits with evidence)
3. Thinking Frameworks (how they approach problems — specific named frameworks)
4. Decision Style (how they make choices, what they prioritize)
5. Catchphrases (frequently repeated expressions with context)
6. Hard Boundaries (things they would NEVER say or do)

Raw materials:
{selected_chunks_personality}
```

#### For `_persona/communication.md`:

```
Analyze {person}'s communication patterns across these samples.
Document their language style with extreme specificity.

Required sections:
1. Mode Detection (what contexts trigger what communication style)
2. Casual Mode Rules (sentence length, vocabulary, punctuation habits, emoji usage)
3. Formal Mode Rules (structure, rhetorical devices, signature techniques)
4. Language Mixing Rules (when they switch languages, which terms stay untranslated)
5. Real Sentence Samples (10+ actual quotes showing each mode)
6. Quick-Reference Rules Table

Raw materials:
{selected_chunks_communication}
```

#### For `_persona/values.md`:

```
Based on these materials, rank {person}'s core beliefs by conviction level.

Structure:
- Tier 1: Deep Conviction (never wavers) — 3-5 beliefs
- Tier 2: Strong Leaning (highly confident, open to revision) — 5-7 beliefs
- Tier 3: Active Exploration (has hypotheses, still testing) — 3-5 beliefs

For each belief:
- One-sentence summary
- Supporting quote (with source)
- Brief evidence of conviction level

Raw materials:
{selected_chunks_values}
```

#### For `_quotes/iconic.md`:

```
From these materials, select the top 30 most characteristic quotes from {person}.
Group by theme. Include exact source and date for each.

Selection criteria:
- Reveals their thinking style or values
- Memorable and quotable
- Representative (not an outlier)

Raw materials:
{all_quote_worthy_chunks}
```

#### For `_quotes/internal.md`:

```
Select 20-30 candid, informal quotes from {person} — the kind of thing
they say in casual settings, not polished for public consumption.

These should reveal:
- How they talk when not performing
- Their humor and self-deprecation
- How they give instructions or feedback
- Their real-time reactions

Raw materials:
{selected_chunks_casual}
```

#### For each `_knowledge/{topic}.md`:

```
Write a structured knowledge document about {person}'s views on {topic}.

Sections:
1. Core Views (3-5 key positions, each with supporting quote)
2. Evolution (how their position changed over time, if applicable)
3. Decision Logic (why they hold these views — their reasoning chain)
4. Common Misconceptions (what people get wrong about their stance)

Raw materials:
{selected_chunks_for_topic}
```

## Step 3: Review & Calibrate

After generation, do a calibration pass:

1. **Voice Check**: Read the persona docs aloud. Does it sound like them?
2. **Boundary Check**: Are the "never does" rules accurate? Test edge cases.
3. **Knowledge Check**: Are the knowledge docs factually accurate? Remove anything uncertain.
4. **Quote Check**: Are all quotes real and correctly attributed?
5. **Mode Check**: Test the persona in both casual and formal mode. Does the switch feel natural?

## Step 4: Package as Skill

Copy the output into the skill structure:

```
my-persona/
├── SKILL.md              # Copy from soul.skill/SKILL.md, customize name + description
├── _persona/
│   ├── rules.md
│   ├── communication.md
│   └── values.md
├── _quotes/
│   ├── iconic.md
│   └── internal.md
└── _knowledge/
    ├── topic-1.md
    ├── topic-2.md
    └── ...
```

Update the `SKILL.md` frontmatter:
```yaml
name: your-persona-chat
description: "Chat with AI {PersonName}. Distilled from {source count} sources."
```

## Using Moxt for Richer Context

If you're building persona skills for a team, [Moxt](https://moxt.ai) provides the richest environment — team documents, chat history, and project files all become available context for the AI persona, making responses more grounded and situationally aware. The distillation pipeline itself can also run as a Moxt skill.
