---
name: create-soul
description: >
  从零开始创建一个 AI 人物。交互式引导：输入人物名 → 提供素材（URL/文件/粘贴文本）→ 自动蒸馏 → 输出可直接使用的 skill 目录。
  Activate when: 用户说 /create-soul、"创建人物"、"蒸馏 [某人]"、"create a persona for [name]"。
---

# /create-soul

从原始素材创建一个可对话的 AI 人物。全程交互式引导，零配置。

---

## 流程总览

```
① 确认人物 → ② 采集素材 → ③ 蒸馏 → ④ 组装 skill → ⑤ 验证 → ⑥ 安装指引
```

---

## Step 1: 确认人物

问用户：
1. **人物姓名**（中英文）
2. **一句话描述**（TA 是谁、做什么的）
3. **素材情况**——已有素材（文件/目录路径）还是需要现场采集？

从回答中确定：
- `{person_name}` — 人物名
- `{slug}` — 英文 slug（用于目录名和 skill 名，如 `wei-ran`）
- `{output_dir}` — 输出路径，默认 `./{slug}-soul/`

---

## Step 2: 采集素材

### 如果用户已有素材目录
直接读取，列出文件清单。跳到 Step 3。

### 如果需要现场采集
引导用户逐项提供，按优先级：

**第一优先（必须至少有一类）：**
- 播客/访谈 URL → 用 `collectors/youtube_transcript.py` 拉取
- 博客/文章 URL → 用 `collectors/fetch_url.py` 拉取
- 即刻主页 URL → 用 `collectors/jike_export.py` 拉取

**第二优先（加分项）：**
- Twitter 自助导出包路径 → 用 `collectors/twitter_archive.py` 解析
- 用户直接粘贴的文本（聊天记录、笔记等）

**采集规则：**
- 每个采集脚本的输出存入 `{output_dir}/_raw/` 对应子目录
- 采集完成后输出清单：文件名、类型、字数
- **最低门槛**：至少 5 个素材文件或累计 1 万字。不足时提醒用户补充，但不强制阻断

---

## Step 3: 蒸馏（3-Pass）

### Pass 1: 逐篇阅读 + 标注

读取 `_raw/` 下所有文件。对每篇素材：
1. **完整阅读**（不跳读、不只看前几行）
2. 提取以下信号：
   - 观点与立场（含具体表述）
   - 思维方式（如何推理、举例、下判断）
   - 语言特征（口头禅、句式节奏、用词偏好）
   - 情绪与态度（什么让 TA 兴奋/愤怒/犹豫）
   - 值得保留的原话（quote-worthy）
3. 按类型标注：人格信号 / 知识信号 / 混合

**检查点**：输出阅读进度，确认每篇都读了。

### Pass 2: 聚合 + 去重

按主题聚合所有信号：
- 合并语义重复的观点（保留表达最好的版本）
- 识别核心主题（3-8 个）
- 标注立场演变（同一话题不同时期的表态）
- 筛选 top 引语（≥20 条）

### Pass 3: 结构化写作

将聚合结果写入以下文件：

#### `_persona/rules.md`
- 身份信息（现在做什么、过去做过什么、公众存在感）
- 核心人格特质（5-8 条，每条附证据）
- 思维框架（TA 特有的分析方式，不是通用框架）
- 决策风格
- 口头禅（原话）
- 硬边界（TA 绝对不会说/做的事，≥5 条）

#### `_persona/communication.md`
- 语言模式（至少区分 2 种场景，每种附 ≥8 条真实句式样本）
- 长文 vs 短文的风格差异
- 口语特征（如果有播客素材）
- 标点和排版习惯
- 语言混用规则（中英文切换习惯）

#### `_persona/values.md`
- 分层级排列信念（深度信仰 / 强倾向 / 探索中）
- 每条附原话引用
- 信念演变轨迹（如果素材跨时间段）

#### `_knowledge/{topic}.md`（每个核心主题一个文件）
- 核心观点（附原话）
- 观点演变
- 推理链路（TA 为什么这么想）

#### `_quotes/iconic.md`
- ≥20 条代表性引语，按主题分组
- 标注来源

#### `_quotes/internal.md`（如果有非正式素材）
- 私下/随意场合的原话
- 展示 TA 不端着时的样子

#### `_meta/sources.md`
- 素材清单 + 覆盖率

---

## Step 4: 组装 SKILL.md

在 `{output_dir}/` 根目录生成 `SKILL.md`：

```markdown
---
name: {slug}-chat
description: "Chat with AI {person_name}. Distilled from {N} sources."
---

# AI {person_name}

You are **{person_name}**, {一句话描述}.

## Activation

1. Load persona files:

\```
./_persona/rules.md
./_persona/communication.md
./_persona/values.md
./_quotes/iconic.md
./_quotes/internal.md
\```

2. Load knowledge docs on demand — only when the conversation topic matches:

\```
./_knowledge/
\```

## Core Rules

### Identity
{从 rules.md 提取 3-5 条核心身份描述}

### Thinking Style
{从 rules.md 提取思维方式要点}

### Language
{从 communication.md 提取关键语言规则}

### Hard Boundaries
{从 rules.md 提取硬边界清单}

### Catchphrases
{从 rules.md 提取口头禅}

## Start

Use `$ARGUMENTS` as the user's first message and respond in character.
```

---

## Step 5: 验证

### 完整性检查

输出 checklist：
```
□ _persona/rules.md — 身份 + 人格 + 思维框架 + 硬边界 ≥5 条
□ _persona/communication.md — ≥2 种语言模式，每种 ≥8 条真实句式
□ _persona/values.md — 分层信念 + 引用
□ _knowledge/ — ≥2 个主题文件
□ _quotes/iconic.md — ≥20 条引语
□ _meta/sources.md — 素材覆盖率
□ SKILL.md — 完整可用
```

有缺项先补，再继续。

### 还原度测试

用生成的 persona 模拟回答 3 个问题：
1. 一个 TA 擅长领域的观点问题
2. 一个闲聊/轻松话题
3. 一个 TA 可能不懂的领域（测试边界）

输出模拟结果，让用户判断像不像。

---

## Step 6: 安装指引

告诉用户怎么用生成的 skill：

**Claude Code：**
```bash
cp -r {slug}-soul/ ~/.claude/commands/{slug}/
# 然后在 Claude Code 中使用 /{slug}-chat
```

**OpenClaw：**
```bash
cp -r {slug}-soul/ ~/.openclaw/skills/{slug}/
```

**Moxt：**
将 `{slug}-soul/` 目录上传到 Workspace 的 `System/Skills/` 下。

---

## 行为规则

1. **逐篇读完再写**。不允许只扫前几行就开始生成。
2. **原话优先**。communication.md 和 quotes 里必须是素材中的原文，不是 AI 改写。
3. **不编造**。素材里没有的信息，不猜测、不补全。在文件中标注"素材未覆盖"。
4. **硬边界要具体**。不写"不使用低俗语言"这种废话，写"不说 XXX"这种能直接执行的规则。
5. **素材不够就说不够**。如果素材太少（<5 个文件），生成基础版并明确告诉用户哪些维度缺素材。
