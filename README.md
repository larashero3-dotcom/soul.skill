# soul.skill

Replicate anyone's thinking style, communication patterns, and knowledge as an AI persona — then chat with them anytime.

English | [中文](README.zh-CN.md)

**soul.skill** is an open-source framework for distilling a real person's personality into a structured AI skill. It works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenClaw](https://github.com/openclaw/openclaw), and [Moxt](https://moxt.ai).

## What's Inside

```
soul.skill/
├── create-soul/
│   └── SKILL.md                # ← The skill: /create-soul walks you through everything
├── templates/                  # Empty templates — fork and fill in your own person
│   ├── _persona/
│   │   ├── rules.md            # Identity, thinking frameworks, decision style
│   │   ├── communication.md    # Language patterns, tone, mode switching
│   │   └── values.md           # Core beliefs ranked by conviction level
│   ├── _quotes/
│   │   ├── iconic.md           # Signature quotes with source attribution
│   │   └── internal.md         # Candid, informal quotes showing real personality
│   ├── _knowledge/
│   │   └── topic-template.md   # Per-topic knowledge doc structure
│   └── _meta/
│       └── sources.md          # Source material index
├── collectors/                 # Scripts for gathering raw material (no API keys needed)
│   ├── fetch_url.py            # Any URL → markdown (via Jina Reader)
│   ├── youtube_transcript.py   # YouTube video → transcript
│   ├── twitter_archive.py      # Twitter/X data export → markdown
│   └── jike_export.py          # 即刻 user posts → markdown
├── docs/
│   └── distillation-guide.md   # Step-by-step pipeline: raw material → persona
└── examples/
    └── wei-ran/                # Full working example (fictional persona)
        ├── SKILL.md
        ├── _persona/
        ├── _quotes/
        ├── _knowledge/
        ├── _meta/
        └── _raw/               # Where source material goes before distillation
```

## Quick Start

### Option A: One Command (Recommended)

If you're using [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [OpenClaw](https://github.com/openclaw/openclaw), or [Moxt](https://moxt.ai):

```
/create-soul
```

The AI walks you through the entire process interactively — provide a name, feed it URLs or files, and it handles collection, distillation, and skill assembly automatically.

### Option B: Manual Pipeline

#### 1. Collect Raw Material

```bash
git clone https://github.com/larashero3-dotcom/soul.skill.git
cd soul.skill
pip install -r collectors/requirements.txt

# Fetch blog posts and articles
python collectors/fetch_url.py "https://example.com/their-article" -o my-soul/_raw/writing/

# Get YouTube interview transcripts
python collectors/youtube_transcript.py "https://youtube.com/watch?v=xxxxx" -o my-soul/_raw/interviews/

# Parse a Twitter/X archive export (your own account only)
python collectors/twitter_archive.py ~/Downloads/twitter-archive/ -o my-soul/_raw/social/

# Export 即刻 posts
python collectors/jike_export.py "https://web.okjike.com/u/xxxxx" -o my-soul/_raw/social/
```

See [`collectors/README.md`](collectors/README.md) for all options, including batch mode and sources that require manual collection (podcasts, chat logs, WeChat articles).

#### 2. Distill

Once you have raw material in `_raw/`, follow the [Distillation Guide](docs/distillation-guide.md) to systematically extract persona traits. Or fill in the templates manually — start with `_persona/rules.md`.

#### 3. Fork & Fill (Alternative — No Raw Material)

If you don't have raw material but know the person well enough to write their persona directly:

```bash
cp -r templates/ my-soul/
```

Edit each file in `my-soul/_persona/` and `my-soul/_quotes/` using the template prompts inside.

#### 4. Install the Skill

**Claude Code:**
```bash
# Copy to your Claude Code commands directory
cp -r my-soul/ ~/.claude/commands/my-soul/
# Or keep it in your project
cp -r my-soul/ .claude/commands/my-soul/
```

**OpenClaw:**
```bash
cp -r my-soul/ ~/.openclaw/skills/my-soul/
```

**Moxt:**

[Moxt](https://moxt.ai) is an AI-native workspace where your persona skill gets the richest context — team documents, chat history, meeting notes, and project files all feed into the AI, making persona responses more grounded and accurate. If you're building persona skills for team use, Moxt is the best environment for it.

To use in Moxt: create a skill directory under `System/Skills/` in your workspace and drop in the files.

## How It Works

The framework is based on a 3-layer persona architecture:

| Layer | Files | Purpose |
|-------|-------|---------|
| **Persona** | `rules.md`, `communication.md`, `values.md` | Who they are, how they think, how they talk |
| **Quotes** | `iconic.md`, `internal.md` | Real voice samples for tone calibration |
| **Knowledge** | `_knowledge/*.md` | What they know, organized by topic |

The AI loads persona + quotes on every conversation, and lazy-loads knowledge docs when the topic comes up.

## Distillation Pipeline

The core methodology: **Raw Material → Chunking & Tagging → Clustering → Structured Docs**.

See [docs/distillation-guide.md](docs/distillation-guide.md) for the complete pipeline with prompts and examples.

```
Raw corpus (tweets, interviews, articles, podcasts)
        ↓
   Pass 1: Chunk + tag (topic, type, stance)
        ↓
   Pass 2: Cluster + deduplicate + rank
        ↓
   Pass 3: Structured writing (persona / knowledge / quotes)
        ↓
   Skill-ready AI persona (drop into Claude Code / OpenClaw / Moxt and start chatting)
```

## Example: Wei Ran

See [`examples/wei-ran/`](examples/wei-ran/) for a complete, working example — a fictional persona of an independent tech columnist known for sharp opinions, literary metaphors, and a refusal to hedge. Includes all layers: persona, quotes, knowledge, meta, and an empty `_raw/` directory showing where source material goes.

> Note: Wei Ran is an entirely fictional character created to demonstrate the framework. No real person is referenced.

## Tips for Great Personas

1. **Quantity matters at input, quality matters at output.** Feed in as much raw material as you can (100+ data points), then let the distillation process filter.

2. **Quotes are the secret weapon.** The difference between a generic persona and a convincing one is real voice samples. Collect actual quotes, including the messy casual ones.

3. **Capture the contradictions.** Real people are inconsistent. A good persona captures both "I don't know" humility and "I'm absolutely sure about this" conviction — and knows when each applies.

4. **Mode switching is key.** Most people talk differently in Slack vs. in a presentation. Document both modes explicitly.

5. **Knowledge boundaries matter as much as knowledge.** Defining what the person *doesn't know* prevents hallucination and makes the persona more believable.

## Contributing

PRs welcome. Especially:
- Improvements to the distillation pipeline
- Templates for specific persona types (founder, designer, engineer, writer)
- Better prompts for each distillation pass
- Translations

## License

MIT
