# seo-optimize - Documentation

> Back to [README](../README.md)

## Prerequisites

- An agent harness that loads `SKILL.md` skills and runs shell commands
- Web search, WebFetch, and an interactive option-picker tool (such as `AskUserQuestion`) in that harness
- Python 3.10 or higher (`analyze_seo.py` uses only the standard library)
- Outbound network access (Step 1 research must fetch primary sources live)
- `gh` CLI (optional; only for the user to run repo metadata commands listed in the plan)

Without network access, the skill states that this run relies on the `knowledge_anchors.md` snapshot date instead of silently reusing it.

## Installation

`<skills-dir>` is the skill directory your harness scans.

### Clone from GitHub

```bash
git clone https://github.com/agenvoy/skill-seo-optimize.git \
    <skills-dir>/seo-optimize
```

### Verify Installation

```bash
ls <skills-dir>/seo-optimize/SKILL.md
python3 <skills-dir>/seo-optimize/scripts/analyze_seo.py . > /dev/null && echo ok
```

Once installed, invoke it in your harness with `/seo-optimize`.

## Configuration

### Project Target Settings (`config.json`)

On the first run, Step 3 asks for the targets and writes them to `{PROJECT_PATH}/.doc/seo-optimize/config.json`. Later runs load the file and restate the current settings in one line; `--reset` deletes it and asks again.

```json
{
  "primary_keywords": ["go scheduler", "golang cron library"],
  "secondary_keywords": ["task scheduling", "fsnotify hot reload"],
  "locales": ["en", "zh-Hant"],
  "locale_policy": "per-language-full",
  "engines": ["google", "google-ai", "chatgpt", "perplexity", "claude"],
  "has_physical_location": false,
  "domain": "https://example.com"
}
```

| Field | Source | Description |
|-------|--------|-------------|
| `primary_keywords` | Prompt | 3–4 candidates derived from reading the source; multi-select or free text |
| `secondary_keywords` | Prompt | Secondary keywords |
| `locales` | Existing language versions | Filled from the language versions the project actually has |
| `locale_policy` | Fixed | `per-language-full`: every language version is optimized fully and weighted equally |
| `engines` | Fixed | Google Search, AI Overviews / AI Mode, ChatGPT, Perplexity, Claude |
| `has_physical_location` | Prompt | `true` triggers `LocalBusiness` schema and Google Business Profile advice |
| `domain` | git remote / `Sitemap:` in `robots.txt` / existing canonical / deploy config | Asked from the user when none of these resolve it; never a placeholder domain |

### Fixed Defaults (Never Asked)

| Item | Fixed Value | Effect |
|------|-------------|--------|
| Region / language | Full optimization per language version | Title, description, JSON-LD, and `og:locale` are written in each page's own language; `x-default` favors no language |
| Target engines | All | OAI-SearchBot is an HTML-only parser, so "main content exists in the initial HTML" always ranks first and CSR-only sites are Critical |

## Usage

### Basic

```bash
/seo-optimize
```

Runs the full pipeline on the current directory: research → analyze → ask → targeted research → plan → confirm → apply → verify.

### Plan Only

```bash
/seo-optimize --plan
```

Stops at Step 4 after writing `{yyyy-MM-dd_HH-mm}-plan.md`, without modifying any project file.

### Target a Project and Reset Goals

```bash
/seo-optimize ./my-site --reset
```

Deletes `./my-site/.doc/seo-optimize/config.json` and asks for keywords and locality again.

### Run the Analyzer Manually

```bash
python3 <skills-dir>/seo-optimize/scripts/analyze_seo.py ./my-site \
    | jq '{code_type, web_surfaces, crawler_directives}'
```

A missing path prints `{"error": "Path does not exist: ..."}`; running without an argument prints usage and exits with code `1`.

### Output Files

```
my-site/.doc/seo-optimize/
├── config.json
├── research-2026-09-24.md
├── 2026-09-24_14-30-plan.md
└── 2026-09-24_14-30-applied.md
```

All output lands in `.doc/seo-optimize/`, never in the project root; after writing, the skill reminds the user to decide whether `.doc/` belongs in `.gitignore`.

## CLI Reference

### Slash Command Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `PROJECT_PATH` | Current directory | Project root |
| `--plan` | — | Produce the plan only; modify no files |
| `--reset` | — | Delete `config.json` and ask for targets again |

### Workflow

| Step | Name | Output / Behavior |
|------|------|-------------------|
| 1 | Research | Phase A: eleven parallel queries plus live fetch of five primary pages (Google, OpenAI, Anthropic); writes `research-{date}.md` |
| 2 | Analyze | Mechanical inventory by `analyze_seo.py` plus reading the source to determine purpose, audience, domain, and README ownership |
| 3 | Ask | Keywords and locality, written to `config.json` |
| 3.5 | Targeted research | Phase B: extra queries per keyword, language, locality, and project type |
| 4 | Plan | `{ts}-plan.md`, summarized to the user, waiting for explicit confirmation |
| 5 | Apply | Applies only items listed in the plan and not rejected |
| 6 | Verify | `{ts}-applied.md` plus the self-check list |

### Research Source Tiers

| Tier | Source | Trust |
|------|--------|-------|
| 1 | `developers.google.com/search`, `web.dev`, OpenAI / Anthropic / Perplexity crawler docs, `schema.org` | Highest; overrides every other tier |
| 2 | Quantitative studies from SE Ranking / Ahrefs / Semrush, GEO academic papers | High; sample size and date must be noted |
| 3 | Search Engine Land, Search Engine Journal, named consultants | Medium; supplementary interpretation only |
| 4 | AEO / GEO SaaS vendor guides | Not trusted by default (conflict of interest) |

### Analyzer Output JSON

| Field | Description |
|-------|-------------|
| `code_type` | `library` / `cli` / `web-app` / `docs-site` / `static-site` / `unknown` |
| `web_surfaces` | Deployable sites grouped by directories such as `public` / `dist` / `docs` (`root`, `page_count`, `has_index`, `kind`) |
| `web_framework` | Detected from config files: `next`, `astro`, `nuxt`, `sveltekit`, `docusaurus`, `mkdocs`, `hugo`, `jekyll`, `vitepress`, `gatsby`, `remix`, `vite` |
| `deploy_targets` | Deploy configs present at the root (`wrangler.toml`, `vercel.json`, `netlify.toml`, `Dockerfile`, etc.) |
| `git_remote` | First remote URL in `.git/config` |
| `package_metadata` | name, description, and keywords from npm / Go module / PyPI / Packagist |
| `crawler_directives` | robots.txt location, user-agents, blocked training and retrieval bots, `Sitemap:` directives, sitemap files, sitemap generators, llms.txt, manifest |
| `metadata_apis` | Where metadata is authored (Next `metadata` / `generateMetadata`, `useSeoMeta`, `useHead`, `<svelte:head>`, Helmet, inline JSON-LD, hreflang) and IndexNow calls |
| `pages` | Per HTML page: title, description, canonical, lang, robots, OG, Twitter, JSON-LD types and parse failures, `jsonld_date_modified`, `data_nosnippet` count, `site_verification` (`google` / `bing`), `csr_shell`, hreflang, h1, h2 count, word count (up to 200 entries) |
| `contents` | Per Markdown file: frontmatter title / description / keywords, h1, word count (up to 200 entries) |
| `existing_config` | Path of an existing `config.json`; empty string otherwise |

CJK text is counted per character and Latin text per word. `csr_shell` is `true` when a page holds only an empty `#root` / `#app` / `#__next` / `#__nuxt` / `#svelte` mount point and fewer than 50 words.

### Rule Routing

| Situation | Active Rules |
|-----------|--------------|
| `web_surfaces` not empty | R1–R7, R10–R12 |
| `code_type` is `library` or `cli` | R8–R10 |
| Both | All, with descriptions and keywords kept consistent across both |
| `library` / `cli` without a web surface | States there is no web SEO surface; R8–R10 only |

### Rules

| Rule | Scope | Trigger |
|------|-------|---------|
| R1 | Title | Empty, over 60 characters (30 CJK), duplicated, or missing the primary keyword |
| R2 | Meta description | Missing, over 160 characters (80 CJK), identical site-wide, or equal to the title |
| R3 | Canonical / robots meta / lang / hreflang | Missing or wrong canonical, missing `lang`, unintended `noindex` or `nosnippet` (confirmed before change), missing or non-reciprocal hreflang on multilingual sites |
| R4 | Open Graph / Twitter Card | Any of `og:title` / `og:description` / `og:image` / `og:url` missing |
| R5 | Heading hierarchy | h1 count ≠ 1, h1 unrelated to title, long page without h2, main content indistinguishable from navigation |
| R6 | JSON-LD | Content matches a schema type but is unmarked, existing markup fails to parse, or content pages lack `dateModified` |
| R7 | robots.txt / sitemap / llms.txt | Site-wide block, blocked retrieval bots, missing sitemap; llms.txt only for agent-facing developer docs |
| R8 | Package registry | Empty description or missing keyword, empty keywords (max 8; Go has no keywords field) |
| R9 | GitHub / README | Empty repo description, no topics, README's first two sentences don't state the purpose |
| R10 | Entity consistency | Project or author name spelled in three or more mismatched ways |
| R11 | Initial HTML | `csr_shell` is `true`: main content appears only after JavaScript runs |
| R12 | Index submission and measurement | Google Search Console or Bing Webmaster Tools unverified, no sitemap, or a deploy pipeline without IndexNow |

### Crawler Classes

| Class | User-agent | Effect of Blocking |
|-------|------------|--------------------|
| Training | `GPTBot`, `ClaudeBot`, `Google-Extended`, `Applebot-Extended`, `Meta-ExternalAgent`, `Bytespider`, `CCBot`, `anthropic-ai`, `cohere-ai`, `Amazonbot` | Opts out of model training only; citations unaffected |
| Retrieval | `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User`, `Googlebot`, `Bingbot`, `Applebot`, `DuckAssistBot` | Forfeits citation eligibility in that engine |
| User-triggered | `Google-Agent`, `ChatGPT-User`, `Perplexity-User` (`Claude-User` is the exception and honors robots.txt) | robots.txt blocks have no effect; enforce at the CDN / WAF layer |

`User-agent: *` with `Disallow: /` counts as blocking both training and retrieval bots. `Google-Extended` does not affect AI Overviews / AI Mode.

### Severity

| Level | Criteria |
|-------|----------|
| Critical | Page cannot be indexed or cited: site-wide Disallow, unintended noindex, blocked retrieval bots, wrong canonical, main content only in CSR |
| High | Key pages missing title / description / h1, JSON-LD parse failures, or multilingual site without hreflang |
| Medium | Missing sitemap, missing OG, messy heading hierarchy, empty registry metadata, unverified GSC / BWT, content pages without `dateModified` |
| Low | Length overruns, inconsistent entity names, missing `Sitemap:` directive |

### Forbidden Actions

| Anti-pattern | Reason |
|--------------|--------|
| Keyword stuffing | Triggers spam classification |
| Mass near-duplicate pages for query variants | Scaled content abuse |
| Marking up content absent from the page (fake FAQ, fake ratings) | Structured data spam |
| Generating llms.txt for non-agent-facing sites and claiming SEO benefit | Contradicts Google's official position |
| Promising ranking or traffic growth | Unverifiable |
| Page-level optimization with no web surface | Hallucination |
| Changing `noindex`, robots.txt blocks, or remote repo metadata without confirmation | Operational decisions with visible consequences |
| Updating dates when content has not changed | Manipulates freshness signals |
| Rewriting existing content with "GEO tricks" | No stable cross-platform causal evidence; may hurt retrieval |
| Serving different content to AI bots by user-agent | Cloaking |

### Apply Boundaries

| Item | Behavior |
|------|----------|
| Changes outside the plan | Never made |
| Items marked "needs user decision" | Untouched until answered |
| `gh repo edit` | Listed for the user to run |
| README managed by a generator | Only the suggested short-description change is reported; structure untouched |
| git | No `commit` / `push` / `tag` |
