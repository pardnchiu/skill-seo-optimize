# Research Protocol

**Phase A（SEO／AEO／GEO 研究報告）：有 3 日內生成的報告則沿用，沒有就必須完整跑一次；Phase B、C 依 SKILL.md 條件執行。**禁止沿用超過 3 日的報告、禁止僅憑模型內建知識作答。

**為何強制：** SEO / AEO 的有效做法半年內會反轉。2025 年多數指南主張「加 llms.txt 提升 AI 可見度」，2026-05-15 Google 官方指南明文表示 llms.txt 被忽略；同一份官方文件也推翻了「特定 schema 類型可觸發 AI 引用」的說法。依賴快取知識會直接產出反效果的優化動作。

---

## 時間窗

| 項目 | 規則 |
|---|---|
| 取得今日日期 | `date +%Y-%m-%d`（禁止假設當前日期） |
| 近半年起點 | `date -v-6m +%Y-%m` (macOS) / `date -d '6 months ago' +%Y-%m` (Linux) |
| 採信範圍 | 起點之後發布或更新的內容 |
| 例外 | Tier 1 官方文件即使發布較早，只要現行仍生效即採信（須確認頁面未被標記 deprecated） |

---

## Phase A：landscape research（Step 1，固定執行）

### A-1 必跑查詢集

全部並行送出。查詢字串中的 `{YYYY}` 以當前年份代入。

| # | 查詢 | 要回答的問題 |
|---|---|---|
| 1 | `Google Search Central {YYYY} AI Mode AI Overviews official guidance update` | 官方立場有無變動 |
| 2 | `AEO answer engine optimization best practices {YYYY}` | 業界當前主張 |
| 3 | `technical SEO checklist {YYYY} structured data AI crawlers` | 技術面清單變動 |
| 4 | `AI crawler user agents robots.txt {YYYY} GPTBot ClaudeBot PerplexityBot OAI-SearchBot` | crawler token 名單變動 |
| 5 | `how ChatGPT Perplexity Claude cite sources {YYYY} study citation data` | 各引擎檢索與引用機制 |
| 6 | `Core Web Vitals {YYYY} thresholds LCP INP CLS` | 效能門檻變動 |
| 7 | `schema.org structured data {YYYY} deprecated rich results changes` | schema 支援變動 |
| 8 | `llms.txt {YYYY} adoption support Google OpenAI Anthropic` | llms.txt 現況 |
| 9 | `Bing Webmaster Tools AI Performance IndexNow ChatGPT {YYYY}` | Bing 索引與 ChatGPT / Copilot 檢索關係、BWT 報告變動 |
| 10 | `generative engine optimization GEO survey arxiv {YYYY}` | GEO 學術證據現況（哪些技巧有可重現效果） |
| 11 | `Google spam policy generative AI responses {YYYY}` | 操弄 AI 回答的處分範圍變動 |
| 12 | `deprecated OR ignored SEO meta tags structured data properties {YYYY}` | 過時參數：已廢棄、被引擎忽略或不再著重的 meta、schema 屬性、指令 |

### A-2 必抓一手來源

以 WebFetch 實際抓取，**不得憑搜尋摘要代替**：

| URL | 抓取目的 |
|---|---|
| `https://developers.google.com/search/docs/fundamentals/ai-optimization-guide` | Google 對 AI 搜尋優化的現行立場（逐條列出建議） |
| `https://developers.google.com/search/updates` | 近半年文件變更清單 |
| `https://developers.openai.com/api/docs/bots` | OpenAI 各 user-agent 用途與 robots.txt 行為 |
| `https://support.claude.com/en/articles/8896518` | Anthropic 各 crawler 用途與 robots.txt 行為 |
| `https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers` | Google 使用者觸發型 fetcher 清單（含 `Google-Agent`） |

若上述 URL 404 或改版，記錄實際狀況並改抓 Google Search Central 首頁找對應新頁面。**不得因抓不到就跳過本步驟並沿用記憶。**

### A-5 標準與提案追蹤（固定執行）

目的：偵測 AI 讀取／使用控制機制在標準組織與主要廠商的最新狀態，與 knowledge_anchors **A12** 追蹤表逐列比對。只看搜尋摘要不算數，下列頁面一律實際抓取；datatracker 與 IANA 優先抓原始資料（JSON API、CSV），因為摘要工具會改寫欄位。

| # | 實抓來源 | 要回答的問題 |
|---|---|---|
| S1 | `https://www.iana.org/assignments/well-known-uris/well-known-uris-1.csv` | 與 AI、agent、bot、LLM、content usage、MCP 相關的 `/.well-known/` 後綴有無新增或狀態變動（provisional → permanent） |
| S2 | `https://datatracker.ietf.org/wg/aipref/documents/`、`https://datatracker.ietf.org/wg/aipref/about/` | aipref vocab／attach 的最新版號、是否進入 WGLC、送 IESG、成為 RFC；有無新採納的 draft |
| S3 | `https://datatracker.ietf.org/wg/webbotauth/documents/` | Web Bot Auth 進度；是否新增網站端需要做的事 |
| S4 | `https://llmstxt.org/` | llms.txt 規格版本與修改日 |
| S5 | `https://developers.cloudflare.com/bots/additional-configurations/managed-robots-txt/` | Cloudflare Content Signals 語法與詞彙 |
| S6 | `https://modelcontextprotocol.io/community/working-groups/server-card` | MCP Server Card 的 well-known 路徑是否定案 |
| S7 | A-2 的 Google／OpenAI／Anthropic crawler 頁，加 Bing Webmaster Blog | 是否有廠商官方宣告支援 `Content-Usage`、Content-Signal、TDMRep、llms.txt |

追加查詢（並行）：

| 查詢 | 要回答的問題 |
|---|---|
| `IETF Internet-Draft AI crawler OR "AI preferences" OR "agent discovery" {YYYY}` | A12 以外的新 draft；個人 draft 被 WG 採納 |
| `W3C community group OR working group AI agents web content {YYYY}` | W3C 新成立或升級的工作 |
| `".well-known" AI agent OR LLM discovery proposal {YYYY}` | 新的 well-known 提案 |

判讀規則：

| 狀態變化 | 動作 |
|---|---|
| 與 A12 相同 | digest 記「無變動」 |
| 版號／日期更新但階段未變（仍為 draft） | 更新 A12，不改規則 |
| 進入可實作門檻：成為 RFC、W3C Recommendation、IANA permanent，或主要廠商官方頁宣告支援 | 更新 A12、在 optimization_rules 新增或修改規則；適用於本專案者列入規劃；由共用範本產生者列為改範本 |
| 語法或路徑改變（如 header 名、檔案路徑） | 已實作者列為 High 修正項，範本同步 |
| 被撤回、Replaced、或廠商宣告不支援 | 更新 A12；已實作者列為可移除項 |

### A-3 來源分級（衝突時的裁決順序）

| Tier | 來源 | 採信度 |
|---|---|---|
| **1** | 搜尋引擎／模型廠商一手文件：`developers.google.com/search`、Google Search Central Blog、`web.dev`、OpenAI / Anthropic / Perplexity 的 crawler 與 bot 文件、`schema.org` | 最高，直接推翻其他層級 |
| **2** | 具方法論與樣本數的量化研究：SE Ranking / Ahrefs / Semrush / Whitespark 的 data study、學術論文（Princeton / IIT Delhi GEO 系列） | 高；須在 digest 標註樣本數與時間 |
| **3** | 從業者評論：Search Engine Land、Search Engine Journal、具名顧問部落格 | 中；僅作為 Tier 1/2 的補充解讀 |
| **4** | AEO / GEO SaaS 廠商的「{YYYY} Ultimate Guide」 | 預設不採信——販售 AEO 工具者對「AEO 是獨立學科」有利益衝突 |

### A-4 衝突處理（強制）

Tier 3/4 的主張與 Tier 1 衝突時：

1. **不得**寫入 digest 的「可執行做法」
2. **必須**寫入 digest 的「業界迷思」欄，附上被推翻的 Tier 1 出處與日期
3. 若該迷思已存在於專案（例：為 AI 塞的直答塊樣板），列為「可移除項」而非「已完成項」

---

## Phase B：競品研究（Step 2.5，設計關鍵字前執行）

輸入為 Step 2 產出的 seed 詞（每語言 2–4 個，描述使用者遇到的問題或要找的工具類型）。三個來源並行收集，**每個 seed × 每個語言**各跑一次：同一概念在中英文的競爭態勢與用詞常完全不同，共用一份結論會誤判。

| # | 來源 | 取法 | 記錄欄位 |
|---|---|---|---|
| B-1 | 搜尋第一頁 | WebSearch `{seed}` | 前 10 名的 URL、頁面型態（清單／教學／工具頁／repo／論壇）、title、description 用詞 |
| B-2 | GitHub 高星同類 | `gh api "search/repositories?q={seed}&sort=stars&order=desc&per_page=10" -q '.items[] \| {full_name,description,stargazers_count,topics,homepage,pushed_at}'`，逐一查詢間隔 2 秒 | full_name、星數、description、topics、homepage、最近 push |
| B-3 | Hacker News 熱門文章 | `curl -s "https://hn.algolia.com/api/v1/search?query={seed}&tags=story&numericFilters=points%3E50&hitsPerPage=10"` | title、points、num_comments、created_at、url |

| 邊界 | 規則 |
|---|---|
| topics 來源 | 用 `gh api search/repositories`；`gh search repos --json` 沒有 topics 欄位 |
| 語意不符的結果 | 排除與本專案不同類的結果（例：seed 為終端機監控工具時，TLS 函式庫排除，SaaS 監控服務保留），並在 digest 註明排除原因 |
| HN 無結果 | 記「無 points > 50 的 story」，不放寬門檻硬湊 |
| ZH seed | B-2、B-3 以 ZH seed 常無結果；仍須跑一次並如實記錄，不以 EN 結果代替 ZH |

### B-4 競品用詞（必跑）

競品的品牌名與它們自己用的類別詞，十之八九就是該領域的熱門詞；只看 seed 的第一頁會漏掉它們。

| 步驟 | 取法 | 記錄欄位 |
|---|---|---|
| 確定競品清單 | 至少 3 個：使用者點名者全部列入（先查證名稱實際指哪個產品，拼錯或俗稱要確認，不猜）；不足 3 個時從 B-1／B-2 反覆出現、被當比較基準的產品中，以品牌名熱度（B-5，EN 全球）與 GitHub 星數排序取最熱門者補滿 | 產品、官方站／repo、熱度、★、判定依據 |
| 分類 | 依部署型態（雲端／本地／自架／SaaS 等）與本專案同型或異型歸類 | 類型、與本專案同型或異型 |
| 收集用詞 | curl 官方首頁原始 HTML 取 `<title>`、meta description、H1；`gh api repos/{owner}/{repo}` 取 description、topics、星數、主要語言 | 原文欄位、它用的類別詞 |
| 用詞數量 | 全部競品合計 EN、ZH 各 ≥ 10 個（品牌名、類別詞、功能詞）；ZH 取自競品繁中頁，沒有則取 ZH 第一頁介紹該競品的頁面用詞，不由 EN 翻譯；不足 10 個時如實記錄缺口 | 詞、語言、出處 |

### B-5 熱度量測（必跑）

以 `scripts/trends.py` 量 Google Trends 相對熱度，候選詞包含：B-4 收集的每個詞（逐詞都量）、seed、本專案能力詞。同一次量測用同一個 anchor（選中等熱度、與專案直接相關的詞），跨批次才可比較。

```bash
python3 -I {skill_dir}/scripts/trends.py --anchor "{anchor}" --geo {GEO,...} --hl {hl} "{term1}" "{term2}" ...
```

| 邊界 | 規則 |
|---|---|
| geo | EN 以英文詞量全球（`--geo WW --hl en-US`）；ZH 以台灣繁中詞量台灣（`--geo TW --hl zh-TW`）；不以其他地區結果代替 |
| 欄位 | `avg`（12 個月平均）、`recent12w`（近 12 週）、`recent4w`（近 4 週）都記錄；新品上市造成的近期暴衝看 `recent12w`、`recent4w` |
| 被限流（`[Unavailable]`／`[Limit]`） | 間隔後重跑；仍失敗則 digest 記「熱度未量」，該詞不得以熱度為理由入選 |
| 泛用字 | 一般英文單字（如 `harness`）的熱度不代表有人在搜本領域，須以詞組重量（`ai harness`） |

產出寫入 digest 的「競品研究」段：

```markdown
## 競品研究（Phase B）

### 競品定位
| 產品 | 類型 | 同型／異型 | ★ | Title | Meta description | H1 | 類別詞 |

### 熱度（anchor：{anchor}，{geo}）
| 詞 | avg | recent12w | recent4w | 來源（競品名／競品類別詞／seed／能力詞） |

### 第一頁（{seed}，{locale}）
| 排名 | 頁面型態 | Title | Description 用詞 | URL |

### GitHub 高星同類（{seed}）
| Repo | ★ | Description | Topics |

### Hacker News（{seed}）
| Title | Points | Comments | 日期 | URL |

### 詞彙彙整（{locale}）
| 詞 | 熱度（avg／recent12w／recent4w） | 競品交集 | 出現來源數 | 代表來源 | 本專案具備 | 結論（主要／次要／不採用＋原因） |
```

---

## Phase C：targeted research（Step 3.5，確定關鍵字與在地性後執行）

| 條件 | 追加查詢 |
|---|---|
| 有實體營業地點 | `Google Business Profile {YYYY} ranking factors NAP consistency` |
| 目標引擎含 ChatGPT / Perplexity / Claude | `{keyword}` 直接問一次各引擎的公開介面不可行時，改查 `{topic} most cited sources {YYYY}` |

---

## Digest 產出

Phase A 寫入 `{skill_dir}/.doc/research/{yyyy-MM-dd}.md`（有 3 日內的報告則沿用，不重跑、不重寫）；Phase B／C 寫入 `{skill_dir}/.doc/{網域}/research/{yyyy-MM-dd}.md`（`{網域}` 規則見 output_format.md「落檔規則」），開頭連到所用的 Phase A 報告。Phase A 報告結構如下：

```markdown
# SEO / AEO 研究摘要（{yyyy-MM-dd}）

## 採信範圍
- 時間窗：{起點} ~ {今日}
- Tier 1 來源實抓：{URL 清單，含抓取結果摘要}

## 官方立場（Tier 1）
| 主題 | 現行立場 | 來源 | 日期 |
|---|---|---|---|

## 量化研究（Tier 2）
| 發現 | 樣本／方法 | 來源 | 日期 |
|---|---|---|---|

## 業界迷思（與 Tier 1 衝突，不採納）
| 主張 | 推翻它的 Tier 1 依據 | 對本專案的意涵 |
|---|---|---|

## 過時參數
| 參數 | 狀態（已廢棄／被忽略／不再著重） | 依據來源（日期） | 建議（移除／保留但最低優先） |
|---|---|---|---|

## 標準追蹤（A-5）
| 名稱 | A12 記錄的狀態 | 本次實抓狀態 | 變化 | 來源 URL |
|---|---|---|---|---|

## 與上次執行的差異
{與 `.doc/research/` 中前一份報告逐項比對並列出變動；無舊檔則寫「首次執行」}

## 本次可執行結論
{條列，每條必須對應到 optimization_rules.md 的某條規則；無對應者刪除}

## 本次發現的新規範
| 規範 | 來源 URL（日期） | skill 原本 | 最新內容 | 本次處理 |
|---|---|---|---|---|
```

**驗證：** digest 中每個「可執行結論」都必須能指到 Tier 1 或 Tier 2 出處。指不到的刪除，不得以「業界普遍認為」保留。
