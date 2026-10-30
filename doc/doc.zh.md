# seo-optimize - 技術文件

> 返回 [README](./README.zh.md)

## 前置需求

- 可載入 `SKILL.md` skill 並執行 shell 指令的 agent harness
- harness 提供網路搜尋、WebFetch 與互動式選項詢問（如 `AskUserQuestion`）工具
- Python 3.10 或更高版本（`analyze_seo.py` 僅使用標準函式庫）
- 對外網路連線（Step 1 研究必須實抓一手來源）
- `gh` CLI（選用；僅用於使用者自行執行規劃中列出的 repo metadata 指令）

網路不可用時，skill 會明確告知本次依據為 `knowledge_anchors.md` 的快照日期，不會靜默沿用。

## 安裝

`<skills-dir>` 為所用 harness 掃描的 skill 目錄。

### 從 GitHub 複製

```bash
git clone https://github.com/agenvoy/skill-seo-optimize.git \
    <skills-dir>/seo-optimize
```

### 確認安裝

```bash
ls <skills-dir>/seo-optimize/SKILL.md
python3 <skills-dir>/seo-optimize/scripts/analyze_seo.py . > /dev/null && echo ok
```

安裝完成後，於 harness 中以 `/seo-optimize` 呼叫即可。

## 設定

### 專案目標設定（`config.json`）

首次執行時由 Step 3 詢問後寫入 `{PROJECT_PATH}/.doc/seo-optimize/config.json`，後續執行直接載入並複述一行目前設定；帶 `--reset` 時刪除後重新詢問。

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

| 欄位 | 來源 | 說明 |
|------|------|------|
| `primary_keywords` | 詢問 | 由原始碼理解產生 3–4 個候選，可複選或自填 |
| `secondary_keywords` | 詢問 | 次要關鍵字 |
| `locales` | 專案實際語言版本 | 依存在的語言版本填寫 |
| `locale_policy` | 固定值 | `per-language-full`：每個語言版本各自完整優化、語言間等權 |
| `engines` | 固定值 | Google 一般搜尋、AI Overviews·AI Mode、ChatGPT、Perplexity、Claude |
| `has_physical_location` | 詢問 | 為 `true` 時觸發 `LocalBusiness` schema 與 GBP 建議 |
| `domain` | git remote／`robots.txt` 的 `Sitemap:`／既有 canonical／部署設定 | 皆推不出時詢問使用者，不填佔位網域 |

### 固定預設（不再詢問）

| 項目 | 固定值 | 影響 |
|------|--------|------|
| 地區／語言 | 每個語言版本各自完整優化 | 各語言的 title／description／JSON-LD／`og:locale` 以該語言撰寫，`x-default` 不偏向任一語言 |
| 目標引擎 | 全部 | 因 OAI-SearchBot 為 HTML-only parser，「主要內容存在於初始 HTML」永遠最高優先，CSR-only 站台列 Critical |

## 使用方式

### 基本用法

```bash
/seo-optimize
```

對當前目錄跑完整流程：研究 → 分析 → 詢問 → 補研究 → 規劃 → 確認 → 套用 → 驗證。

### 只產出規劃

```bash
/seo-optimize --plan
```

流程止於 Step 4，產出 `{yyyy-MM-dd_HH-mm}-plan.md`，不修改任何專案檔案。

### 指定專案並重設目標

```bash
/seo-optimize ./my-site --reset
```

清除 `./my-site/.doc/seo-optimize/config.json`，重新詢問關鍵字與在地性。

### 手動執行分析器

```bash
python3 <skills-dir>/seo-optimize/scripts/analyze_seo.py ./my-site \
    | jq '{code_type, web_surfaces, crawler_directives}'
```

路徑不存在時輸出 `{"error": "Path does not exist: ..."}`；未帶參數時印出用法並以 exit code `1` 結束。

### 產出檔案

```
my-site/.doc/seo-optimize/
├── config.json
├── research-2026-09-24.md
├── 2026-09-24_14-30-plan.md
└── 2026-09-24_14-30-applied.md
```

所有產出皆在 `.doc/seo-optimize/`，不在專案根目錄落檔；寫入後提醒使用者確認 `.doc/` 是否加入 `.gitignore`。

## 命令列參考

### Slash Command 參數

| 參數 | 預設 | 說明 |
|------|------|------|
| `PROJECT_PATH` | 當前目錄 | 專案根目錄 |
| `--plan` | — | 只產出優化規劃，不修改任何檔案 |
| `--reset` | — | 清除 `config.json`，重新詢問目標設定 |

### 工作流程

| Step | 名稱 | 產出／行為 |
|------|------|-----------|
| 1 | 研究 | Phase A：十一組查詢並行＋五個一手頁面（Google、OpenAI、Anthropic）實抓；產出 `research-{date}.md` |
| 2 | 分析 | `analyze_seo.py` 機械盤點＋實讀原始碼判斷用途、使用者、網域、README 管理方 |
| 3 | 詢問 | 關鍵字與在地性，寫入 `config.json` |
| 3.5 | 補研究 | Phase B：依關鍵字、語言、在地性、專案類型追加查詢 |
| 4 | 規劃 | `{ts}-plan.md`，呈現摘要並等待明確確認 |
| 5 | 套用 | 只套用規劃中列出且未被否決的項目 |
| 6 | 驗證 | `{ts}-applied.md`＋自我檢查清單 |

### 研究來源分級

| Tier | 來源 | 採信度 |
|------|------|--------|
| 1 | `developers.google.com/search`、`web.dev`、OpenAI／Anthropic／Perplexity crawler 文件、`schema.org` | 最高，直接推翻其他層級 |
| 2 | SE Ranking／Ahrefs／Semrush 量化研究、GEO 學術論文 | 高；須標註樣本數與時間 |
| 3 | Search Engine Land、Search Engine Journal、具名顧問 | 中；僅補充解讀 |
| 4 | AEO／GEO SaaS 廠商指南 | 預設不採信（利益衝突） |

### 分析器輸出 JSON

| 欄位 | 說明 |
|------|------|
| `code_type` | `library`／`cli`／`web-app`／`docs-site`／`static-site`／`unknown` |
| `web_surfaces` | 依 `public`／`dist`／`docs` 等目錄分組的可部署站台（`root`、`page_count`、`has_index`、`kind`） |
| `web_framework` | 依設定檔偵測：`next`、`astro`、`nuxt`、`sveltekit`、`docusaurus`、`mkdocs`、`hugo`、`jekyll`、`vitepress`、`gatsby`、`remix`、`vite` |
| `deploy_targets` | 根目錄存在的部署設定（`wrangler.toml`、`vercel.json`、`netlify.toml`、`Dockerfile` 等） |
| `git_remote` | `.git/config` 中第一個 remote URL |
| `package_metadata` | npm／Go module／PyPI／Packagist 的 name、description、keywords |
| `crawler_directives` | robots.txt 位置、user-agent、被封鎖的訓練型與檢索型 bot、`Sitemap:` 指令、sitemap 檔、sitemap 產生器、llms.txt、manifest |
| `metadata_apis` | metadata 撰寫位置（Next `metadata`／`generateMetadata`、`useSeoMeta`、`useHead`、`<svelte:head>`、Helmet、inline JSON-LD、hreflang）與 IndexNow 呼叫 |
| `pages` | 每個 HTML 頁的 title、description、canonical、lang、robots、OG、Twitter、JSON-LD 類型與解析失敗數、`jsonld_date_modified`、`data_nosnippet` 數、`site_verification`（`google`／`bing`）、`csr_shell`、hreflang、h1、h2 數、字數（上限 200 筆） |
| `contents` | 每個 Markdown 檔的 frontmatter title／description／keywords、h1、字數（上限 200 筆） |
| `existing_config` | 既有 `config.json` 路徑；無則為空字串 |

CJK 字數以字元個數計算，拉丁文字以單字計算。`csr_shell` 為 `true` 表示頁面只有空的 `#root`／`#app`／`#__next`／`#__nuxt`／`#svelte` 掛載點且字數少於 50。

### 規則路由

| 情境 | 生效規則 |
|------|----------|
| `web_surfaces` 非空 | R1–R7、R10–R12 |
| `code_type` 為 `library` 或 `cli` | R8–R10 |
| 兩者皆成立 | 全部，且兩邊描述與關鍵字須一致 |
| 無 web surface 的 `library`／`cli` | 告知無 web SEO surface，僅 R8–R10 |

### 規則一覽

| 規則 | 範圍 | 觸發判準 |
|------|------|----------|
| R1 | Title | 空、超過 60 字元（CJK 30 字）、重複、未含主要關鍵字 |
| R2 | Meta description | 缺失、超過 160 字元（CJK 80 字）、全站同句、與 title 相同 |
| R3 | Canonical／robots meta／lang／hreflang | 缺 canonical、指向錯誤、缺 `lang`、誤設 `noindex` 或 `nosnippet`（變更前確認）、多語站缺或不互指 hreflang |
| R4 | Open Graph／Twitter Card | 缺 `og:title`／`og:description`／`og:image`／`og:url` 任一 |
| R5 | 標題階層 | h1 數 ≠ 1、h1 與 title 脫節、長頁無 h2、主內容與導覽無法區分 |
| R6 | JSON-LD | 內容符合某 schema 語意但未標註、既有標註解析失敗、內容頁缺 `dateModified` |
| R7 | robots.txt／sitemap／llms.txt | 全站封鎖、封鎖檢索型 bot、缺 sitemap；llms.txt 僅限 agent-facing 開發文件 |
| R8 | 套件登錄頁 | description 空或未含關鍵字、keywords 空（上限 8 個；Go 無 keywords 欄位） |
| R9 | GitHub／README | repo description 空、無 topics、README 前兩句未說明用途 |
| R10 | 實體一致性 | 專案名／作者名在三處以上出現互不對應的寫法 |
| R11 | 初始 HTML | `csr_shell` 為 `true`：主要內容只在 JavaScript 執行後出現 |
| R12 | 索引提交與量測 | 未驗證 Google Search Console 或 Bing Webmaster Tools、無 sitemap、有部署流程卻未接 IndexNow |

### Crawler 分類

| 類別 | User-agent | 封鎖後果 |
|------|------------|----------|
| 訓練型 | `GPTBot`、`ClaudeBot`、`Google-Extended`、`Applebot-Extended`、`Meta-ExternalAgent`、`Bytespider`、`CCBot`、`anthropic-ai`、`cohere-ai`、`Amazonbot` | 僅退出模型訓練，不影響引用 |
| 檢索型 | `OAI-SearchBot`、`ChatGPT-User`、`Claude-SearchBot`、`Claude-User`、`PerplexityBot`、`Perplexity-User`、`Googlebot`、`Bingbot`、`Applebot`、`DuckAssistBot` | 放棄該引擎的引用資格 |
| 使用者觸發型 | `Google-Agent`、`ChatGPT-User`、`Perplexity-User`（`Claude-User` 例外，遵守 robots.txt） | robots.txt 封鎖無效，需在 CDN／WAF 層處理 |

`User-agent: *` 搭配 `Disallow: /` 同時計入訓練型與檢索型。`Google-Extended` 不影響 AI Overviews／AI Mode。

### 嚴重度

| 級別 | 判準 |
|------|------|
| Critical | 頁面無法被索引或引用：全站 Disallow、誤設 noindex、封鎖檢索型 bot、canonical 指錯、主要內容僅存在於 CSR |
| High | 主要頁面缺 title／description／h1、JSON-LD 解析失敗，或多語站缺 hreflang |
| Medium | 缺 sitemap、缺 OG、標題階層混亂、套件登錄頁 metadata 空白、未驗證 GSC／BWT、內容頁缺 `dateModified` |
| Low | 長度超標、實體名稱不一致、缺 `Sitemap:` 指令 |

### 禁止動作

| 反模式 | 原因 |
|--------|------|
| 關鍵字堆砌 | 觸發垃圾內容判定 |
| 為查詢變體大量產生近似頁面 | scaled content abuse |
| 標註頁面上不存在的內容（假 FAQ、假評分） | 結構化資料垃圾 |
| 為非 agent-facing 站台產生 llms.txt 並宣稱有 SEO 效果 | 與 Google 官方立場衝突 |
| 承諾排名或流量成長幅度 | 無法驗證 |
| 無 web surface 時虛構頁面優化 | 幻覺 |
| 未經確認改動 `noindex`、robots.txt 封鎖、遠端 repo metadata | 屬營運決策，誤改後果外顯 |
| 內容未變動卻更新日期 | 操弄新鮮度訊號 |
| 以「GEO 技巧」改寫既有內容 | 無穩定跨平台因果證據，且可能損害檢索 |
| 依 user-agent 對 AI bot 回傳不同內容 | cloaking |

### 套用界線

| 項目 | 行為 |
|------|------|
| 規劃外的修改 | 一律不做 |
| 標為「需使用者決策」的項目 | 未獲答覆前不動 |
| `gh repo edit` | 只列指令，由使用者執行 |
| 由產生器管理的 README | 只回報簡短描述的調整建議，不改寫結構 |
| git | 不執行 `commit`／`push`／`tag` |
