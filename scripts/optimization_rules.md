# Optimization Rules

每條規則格式為：**判準（何時觸發）→ 動作（改什麼）→ 邊界（何時不做）**。

執行 Step 5 時，只允許套用本檔列出的動作。分析結果未命中任何判準時，該面向的正確產出是「未觀察到需處理事項」，不是硬湊建議。

---

## 適用範圍路由

`analyze_seo.py` 回傳的 `code_type` 與 `web_surfaces` 決定哪幾組規則生效。

| 情境 | 生效規則組 |
|---|---|
| `web_surfaces` 非空 | R1–R6（頁面層）＋ R7（爬蟲指令）＋ R10（實體一致性）＋ R11（初始 HTML）＋ R12（索引提交）＋ R13（AI 使用偏好宣告）＋ R14（Favicon）＋ R15（網址遷移與導向）＋ R16（索引範圍） |
| `code_type` ∈ {library, cli} | R8（套件登錄頁）＋ R10 |
| `git remote` 為 `github.com` | R9（GitHub repo description／topics／homepage 與 README 簡短描述），不論 `code_type` 與有無 `web_surfaces` |
| 兩者皆成立（例：Go library 內含文件站） | 全部；且兩邊的專案描述、關鍵字必須一致（R10） |
| `web_surfaces` 為空且 `code_type` ∈ {library, cli} | **明確告知使用者本專案無 web SEO surface**，僅執行 R8、R10（GitHub repo 另執行 R9）。禁止虛構頁面來套用 R1–R7 |

---

## R1 — Title

**判準**：`title` 為空／顯示寬度 > 60（CJK 與全形字元計 2、其餘計 1，`title_length`）／同一 surface 內重複／未含主要關鍵字／**與頁面內容不符**（title 的主題詞不是該頁 h1 與正文實際在講的事）。

**動作**：改寫為 `{主要關鍵字}｜{區分詞}｜{品牌}` 或 `{主要關鍵字} - {品牌}`。

```html
<!-- before -->
<title>Documentation</title>
<!-- after -->
<title>Scheduler API Reference | my-scheduler</title>
```

**邊界**：
- 既有 title 已含關鍵字且長度合宜 → 不動。「換個寫法更順」不是理由
- 品牌名放尾端，以 ` | `（ZH 用 `｜`）分隔；不帶 `{owner}/` 等帳號前綴
- 關鍵字只出現一次。`Scheduler - Go Scheduler - Cron Scheduler` 屬堆砌，禁止
- **內容優先於關鍵字**：關鍵字只放進確實以它為主題的頁面。該頁內文沒有涵蓋的詞（即使熱度高、是 config 的主要關鍵字）不得寫進該頁 title；要用就先讓內容真的涵蓋，否則改放到涵蓋它的頁面或不用
- 驗證：title 中每個主題詞（品牌名除外）都要能在該頁的 h1 或可見正文找到相同或同義的寫法；找不到的列為缺口，不能靠改 title 硬湊

---

## R2 — Meta description

**判準**：缺失／顯示寬度 > 160（CJK 與全形字元計 2、其餘計 1，`description_length`）／整站同一句／與 title 完全重複／**描述了頁面上沒有的內容**（承諾的功能、資訊或答案，點進來找不到）。

**動作**：寫一句描述該頁**實際內容**的句子，含主要關鍵字，說明使用者點進來會得到什麼。

**邊界**：
- description 不是排序因子，作用是點閱率與 AI 摘要素材。禁止塞關鍵字
- description 的每個陳述都要能在該頁可見內容找到對應；寫的是「點進來會得到什麼」，不是「希望被搜到什麼」
- 已存在且準確描述該頁 → 不動
- 大量頁面缺 description 時，**不得**用樣板批次填同一句；改為由該頁 h1 + 首段生成各自的句子，做不到就只處理主要頁面並在報告說明未處理範圍

---

## R3 — Canonical / robots meta / lang

| 判準 | 動作 |
|---|---|
| 無 `<link rel="canonical">` | 加上該頁的絕對 URL（須確認正式網域，不得猜） |
| canonical 指向不存在或非本頁的 URL | 修正 |
| `<html>` 缺 `lang` | 依內容實際語言補上（`zh-Hant-TW` / `en`） |
| `robots` meta 為 `noindex` 但該頁應被索引 | 移除；**移除前必須向使用者確認**該頁確實應公開 |
| 無 `robots` meta | 不動——預設即為可索引，補 `index, follow` 是冗餘 |
| 主要內容頁帶 `nosnippet`、過小的 `max-snippet`，或 `data_nosnippet > 0` 包住主要內容 | 向使用者確認是否有意；這些指令同時移除一般搜尋摘要與 AI Overviews / AI Mode 的輸入資格（A5） |
| 有多語版本但缺 `hreflang` | 每個語言版本列出全部語言（含自身）的 `<link rel="alternate" hreflang>`，並加 `x-default` |
| `hreflang` 不互相對應（A 指向 B，B 未指回 A）或值非合法語言碼 | 修正為雙向且使用 `en` / `zh-Hant` 等 BCP 47 語言碼 |
| 依 `Accept-Language`／IP 自動導向或在同一 URL 動態切換語言 | 改為各語言固定 URL，根路徑回傳固定內容並放可見的語言切換連結；Googlebot 通常自美國抓取且不帶 `Accept-Language`，動態切換的變體可能抓不到（A8 多語站語言判定） |

**邊界**：
- `hreflang` 各語言等權（見 SKILL.md 固定預設），`x-default` 指向語言選擇頁或無語言偏向的入口，不指向任一特定語言
- 正式網域無法從 `git_remote`、`robots.txt` 的 `Sitemap:` 指令、既有 canonical 或 `wrangler.toml` 推得時，**問使用者**，不得填 `https://example.com`。

---

## R4 — Open Graph / Twitter Card

**判準**：缺 `og:title` / `og:description` / `og:image` / `og:url` 任一。

**動作**：補齊四項；`og:type` 依頁面性質（`website` / `article`）；`twitter:card` 用 `summary_large_image` 並確認圖片實際存在於 repo 或可解析的 URL。

**邊界**：
- `og:image` 找不到實際圖檔 → 不得填造出來的路徑。改為在報告列為「需提供 OG 圖」的待辦
- OG 不影響搜尋排序，作用在社群分享與部分 AI 介面的預覽卡
- `og:image` 同時是 Google 預覽圖的訊號之一（A11）：選與頁面相關的代表圖，避開通用圖、含字圖與極端長寬比

---

## R5 — 標題階層與內容結構

**判準**：頁面 h1 數量 ≠ 1／h1 與 title 語意脫節／缺乏 h2 分段（`h2_count == 0` 且 `word_count > 600`）／主要內容與導覽在標記上無法區分。

**動作**：
- 每頁一個 h1，對應該頁主題
- 用語意化標籤標出主要內容（`<main>`、`<article>`）與導覽（`<nav>`）
- 長頁以 h2 分段，標題寫成使用者實際會問的形式（「如何設定 cron 排程」優於「設定」）
- 主要內容預設可見，不藏在折疊區或 tab；頁面載入時不以 JavaScript 控制捲動位置，呼叫 history API 或改 `location.hash` 時保留 URL 的 hash fragment（snippet「Read more」深層連結條件，A4）

**邊界**：
- **禁止**為了 AI 而把每個 section 前面塞「直答塊」樣板，或把長頁拆成大量單一問答頁——見 knowledge_anchors A4，這是被官方點名的反模式
- 既有結構已清楚 → 不動

---

## R6 — 結構化資料（JSON-LD）

**判準**：頁面內容**確實符合**某個 schema.org 類型的語意，且該類型尚未標註；或既有 JSON-LD 解析失敗（`jsonld_invalid > 0`）。

**動作**：加入對應 JSON-LD。類型對照：

| 頁面性質 | 類型 |
|---|---|
| 軟體專案首頁 | `SoftwareApplication` 或 `SoftwareSourceCode` |
| 技術文件 / 教學 | `TechArticle`；有明確步驟者 `HowTo` |
| 部落格文章 | `Article` / `BlogPosting` |
| 站台整體 | `WebSite`＋`Organization`（放首頁） |
| 有實體營業地點 | `LocalBusiness` 子類型＋`address`＋`geo`＋`openingHours` |
| 頁面上**真實存在**的問答區塊 | `FAQPage` |

**邊界（重要）**：
- 標註內容必須與頁面上**可見內容一致**。頁面沒有 FAQ 區塊就標 `FAQPage`、沒有評分就標 `aggregateRating`，屬結構化資料垃圾，會被處分
- **不得**以「提升 AI 引用」為理由加 schema——官方已否定該因果（A2）。理由寫「rich results 資格」或「實體理解」
- `SoftwareApplication` 的 rich result 須有 `offers.price`（免費填 `0`）與真實的 `aggregateRating` 或 `review`（A2）；沒有真實評分／評論者仍可標註，理由寫「實體理解」，不得補評分求資格
- 既有標註正確 → 不動

**Organization 判準**：只為**實際存在**的組織產生 `Organization` 節點——公司登記名稱、有官網或 GitHub org 可對應者。地區、職能、口號等定位文字（例：「City · Software Engineering」）不是組織，放可見署名或 tagline，不得成為 `Organization` 並把作者掛為 `founder`。多語站各語言頁用該語言的正式名稱（例：中文頁用中文登記名、英文頁用英文登記名），另一語言放 `alternateName`，`@id` 共用。作者網站已宣告 Organization 時沿用其 `@id`。（歷史事故：曾有文件站把定位文字宣告為組織，作者網站上沒有對應節點。）

**日期（A10）**：`Article` / `BlogPosting` / `TechArticle` 須帶 `datePublished`，內容曾更新者帶 `dateModified`（`jsonld_date_modified == false` 即觸發），值取自 git 修改時間或**內容雜湊有變動時**的建置日期，並在頁面上可見顯示同一日期。有建置流程者由建置階段寫入：保存每頁內容雜湊與 `published`／`modified`，雜湊改變才更新 `modified`；雜湊涵蓋頁面原文與該頁 title／description／keywords／canonical／hreflang／JSON-LD（不含日期本身），只改 meta 或 JSON-LD 也算內容變動、須更新 `modified`（使用者 2026-10-21 指定：本 skill 改過的頁面，日期一律跟著更新）；sitemap `lastmod` 取同一值。**不得**直接用檔案 mtime 或每次建置的日期——重新產生檔案就會變動，等同內容未變卻更新日期。**禁止**內容未變動時更新日期。

---

## R7 — 爬蟲指令

### R7.1 robots.txt

| 判準 | 動作 | 嚴重度 |
|---|---|---|
| `User-agent: *` + `Disallow: /`（站台應公開） | 移除全站封鎖 | Critical |
| 封鎖了檢索型 bot（`OAI-SearchBot`／`Claude-SearchBot`／`PerplexityBot`／`Googlebot` 等） | 向使用者確認是否有意；非有意則移除 | Critical |
| 無 robots.txt | 建立，含 `Sitemap:` 指令 | Medium |
| 有 robots.txt 但無 `Sitemap:` 指令且 sitemap 存在 | 補指令 | Low |
| 使用者明確表示要退出 AI 訓練 | 逐一列出訓練型 bot（見 A5 表），**不得**用 `*` | — |
| robots.txt 封鎖使用者觸發型 fetcher（`Google-Agent`、`ChatGPT-User`、`Perplexity-User`） | 告知該規則無效（這些 fetcher 忽略 robots.txt，見 A5）；實際需要阻擋者改在 CDN / WAF 層處理 | Low |
| 使用者想退出 AI Overviews 而封鎖 `Google-Extended` | 告知 `Google-Extended` 不影響 AI Overviews / AI Mode；可退出的途徑是 Search Console「Search generative AI」property 層級開關（使用者手動設定，列入「需人工後續」）或 `nosnippet` 系列（同時移除一般摘要），說明兩者代價（A5） | — |
| 新產生的 robots.txt 規則路徑含非 ASCII 字元 | 以 percent-encoded 形式書寫（`/foo/%E3%83%84`）；Google 兩者等價，編碼後第三方工具較易處理（A5，robots-txt-spec 2026-10-23） | — |

### R7.2 sitemap.xml

**判準**：無 sitemap；或 sitemap 存在但頁面數與 `page_count` 明顯不符。

**動作**：產生／更新 sitemap，含 `<lastmod>`。有建置流程者改為在建置階段產生，不手動維護一份會漂移的靜態檔。

**邊界**：sitemap 內的 URL 必須是實際可存取的正式網域路徑；推不出網域就先問。

### R7.3 llms.txt

**判準**：`web_surfaces` 非空即產生，不論是否為 agent-facing 文件（使用者 2026-10-21 指定：SEO／GEO／AEO 面向全部補齊）。

**動作**：於文件站根目錄產生 llms.txt，列出主要文件頁的標題、URL 與一行說明，並依 llms.txt 規格**最新版**（A3、A12）實作其探索機制。研究查到規格新版時，新增的機制一律列入規劃實作，不列為「選用、由使用者決定」。目前（v2）包含：

| 項目 | 內容 |
|---|---|
| 每頁 Markdown 版 | `/{slug}.md`（目錄型 URL 用 `index.md`）；llms.txt 的連結指向 Markdown 版 |
| 探索連結 | 每頁 `<head>` 加 `<link rel="alternate" type="text/markdown" href="...md">` 與 `<link rel="describedby" href="/llms.txt">` |
| 可見連結 | 頁面可見區（如署名列）放 `llms.txt` 與本頁 Markdown 連結——fetch 工具把 HTML 轉成 Markdown 後連結仍在，不跟隨 `<head>` link 的 agent 也找得到 |
| 符號索引 | 函式庫／SDK 文件在 llms.txt 加 `## Symbols`：公開符號 → 記載它的頁面，讓以符號名查文件一次命中 |
| 全文檔 | `llms-full.txt` 依導覽順序串接全部頁面、每段標示來源 URL；多語站每個語言各一份 |
| 編碼 | `.md`、`.txt` 回應的 `Content-Type` 必須帶 `charset=utf-8`（靜態託管常預設不帶，瀏覽器以 Latin-1 解碼，CJK 全成亂碼）；部署後以 `curl -sI` 確認 |

**產生方式（依專案有無建置流程二選一，必須向使用者說明取捨）**：

| 專案型態 | 做法 | 代價 |
|---|---|---|
| 有建置流程（頁面清單由某個 NAV / manifest / frontmatter 驅動） | 在建置階段由該來源產生 | 需改建置腳本；文件增刪自動同步 |
| 無建置流程，或使用者明確表示不動程式 | 直接寫靜態檔 | 不碰程式；**文件增刪時會漂移**，須在報告標明此風險 |

**產出後必須驗證（強制）**：把 llms.txt 內的每個 URL 對照實際頁面（Markdown 版）清單比對，列出「llms.txt 有但頁面無」與「頁面有但 llms.txt 無」兩份差集。llms.txt 是給 agent 讀的入口索引，指向 404 比沒有這個檔更糟——agent 會把它當成權威清單。

**邊界**：
- 任何情況下**不得**宣稱 llms.txt 會提升搜尋或 AI 可見度
- **不得因為「它不影響排名」就在規劃中略過本規則**：`analyze_seo.py` 的 `crawler_directives.llms_txt` 已回報其有無，判準成立時它就是一個待執行項，不是可選的加分題。（歷史事故：曾有一次執行中，llms.txt 因被歸類為「非文字改動」而在套用階段被整項跳過，使用者事後才發現漏掉。）

---

## R8 — 套件登錄頁 metadata（library / cli）

函式庫與 CLI 的「搜尋結果頁」是套件登錄站，不是自家網站。

| 生態 | 可優化欄位 | 判準 |
|---|---|---|
| npm | `description`、`keywords`、`homepage`、`repository` | `description` 為空或未含主要關鍵字；`keywords` 為空 |
| PyPI | `description`、`keywords`、`classifiers`、`project_urls` | 同上 |
| Packagist | `description`、`keywords`、`homepage` | 同上 |
| pkg.go.dev | 套件層 doc comment（`// Package xxx ...`）、README | package 註解缺失或未說明用途；同名套件存在時，註解首句須寫出能區分的用途與作者／組織脈絡 |

**動作**：description 一句話寫清楚「這是什麼 + 解決什麼」；keywords 取 3–8 個使用者實際會搜的詞。

**邊界**：keywords 上限 8 個，塞滿無關詞在多數登錄站會降低相關性評分。Go 沒有 keywords 欄位——**不得**虛構。

---

## R9 — GitHub repo 與 README

GitHub repo 頁是與網站並列的搜尋面（「X alternative」類查詢結果以 GitHub repo 為主），與網站一起依同一組定位優化，不另立方向。

**判準**：`gh repo view {owner}/{repo} --json description,repositoryTopics,homepageUrl` 的實際值有任一不成立：

| 欄位 | 通過條件 |
|---|---|
| description | 等於 config `one_liner.en`（保留既有類型前綴，如 `(module)`） |
| topics | 涵蓋主要關鍵字對應的 GitHub topic（小寫連字號，如 `self-hosted`），GitHub 上限 20 個；每個 topic 的使用 repo 數 ≥ 1,000 |
| homepage | 等於 config `domain`（有網站時） |
| README 簡短描述 | README h1 下方第一個 blockquote，EN／ZH 分別等於 `one_liner.en`／`one_liner.zh` |

**定位句 `one_liner`**：description、README 簡短描述與 topics 的單一來源，寫入 config。

| 欄位 | 條件 |
|---|---|
| `one_liner.en` | 固定格式 `A [tech] [what it is] with [f1], [f2], and [f3]`，≤ 20 個英文單字，句尾無句號；含 config 主要關鍵字至少一個；與網站首頁 description 同一定位 |
| `one_liner.zh` | 同結構以中文撰寫（約 20–26 字），含 ZH 主要關鍵字至少一個，非逐字翻譯 |
| topics | 由同一組主要／次要關鍵字推導；候選取自 research digest「競品研究」中高星同類 repo 的 topics |

config 已有 `one_liner` 且仍符合條件 → 沿用；不符或缺 → 重新設計，於 Step 4 規劃中列出「現況 → 新值」由使用者確認。

**動作**：
- description／topics／homepage 不通過 → 組出單一 `gh repo edit` 指令（`--description`、`--add-topic`、`--homepage`；要移除已偏離定位的 topic 才加 `--remove-topic`），以 `AskUserQuestion` 附完整指令與「現況 → 新值」對照詢問是否更新
- 使用者同意 → 直接執行，再跑一次 `gh repo view` 確認三個欄位已生效；否決 → 指令列入「需人工後續」
- README 簡短描述不等於 `one_liner` → 只替換 `README.md` 與中文 README（`README.zh.md` 或 `doc/README.zh.md`）的簡短描述那一行 blockquote，其餘內容不動

**邊界**：
- README 由產生器管理時，簡短描述列「交由呼叫方」並附 `one_liner`，不直接改；結構與其他段落的建議只回報，交由產生器重生成
- `gh repo edit` 改的是公開的遠端狀態：未經該次 `AskUserQuestion` 同意不得執行；同意只涵蓋問題中列出的那一條指令
- 每個候選 topic 先以 `gh api "search/repositories?q=topic:{topic}&per_page=1" -q .total_count` 查使用 repo 數（逐一查詢間隔 2 秒，避開 search API 每分鐘 30 次限制）：< 1,000 不加；同義詞擇使用數最多的一個（`self-hosted` 40k 優於 `selfhosted` 2k）。詢問時預覽列出每個 topic 的使用數；既有 topic 低於門檻者列為移除候選一併詢問，不自行移除
- topic 的社群語意要與專案相符，不只看字面：查該 topic 頁前幾名 repo 的性質，不同就不加
- topics 不塞與專案無關的熱門詞；description 不堆疊同義詞（禁止動作：關鍵字堆砌）

---

## R10 — 實體一致性

**判準**：專案名／產品名／作者名在下列位置出現不一致寫法。

檢查位置：`package.json` name、`go.mod` module、README h1、網站 `<title>` 品牌段、`og:site_name`、JSON-LD 的 `name`、GitHub repo 名。

**動作**：統一為單一正式寫法，其餘位置對齊。

**Person／Organization 節點的 `sameAs`**：Person `sameAs` 以 `{skill_dir}/.doc/author.json` 的 `same_as` 為必含清單（不存在時以 `AskUserQuestion` 詢問 `author_name`、`author_url`、`same_as` 一次並寫入）（使用者 2026-10-02 指定），每個站台全數放入、不得刪減，作者網站本身也在內；再與作者網站同一 `@id` 節點比對，差異列入人工後續。個人帳號放 Person、組織帳號（GitHub org）放 Organization，不混放。站外網站（作者個人網站、LinkedIn）的對應修改列入「需人工後續」。

**為何**：實體一致是 Tier 2 研究中少數反覆被證實有效的做法（A8）；名稱漂移會讓引擎無法把散落的提及歸戶到同一實體。

**邊界**：
- 大小寫與連字號差異（`my-scheduler` vs `My Scheduler`）若分屬「套件識別碼」與「展示名稱」兩種用途，屬合理差異，不強制統一；真正要抓的是三種以上互不對應的寫法
- 站外品牌提及（YouTube、Reddit、第三方評測）與 AI 可見度高度相關（A8），但無法由修改檔案達成，只列入「需人工後續」

---

## R11 — 主要內容存在於初始 HTML

**判準**：任一頁 `csr_shell == true`（空的 `#root` / `#app` / `#__next` 掛載點且字數 < 50）；或 `web_framework` 為 `vite` 等純 CSR 建置且 index 頁字數極低。

**動作**：改為 SSR、SSG 或建置期 prerender，讓標題、正文、主要表格在未執行 JavaScript 時即存在於 HTML。以 `curl -s {url} | grep` 或停用 JavaScript 瀏覽確認。

**嚴重度**：Critical。OAI-SearchBot 不執行 JavaScript（A6），固定預設的目標引擎含 ChatGPT，內容抓不到時其餘規則皆無意義。

**邊界**：
- 改渲染模式屬架構變更，規劃中只列方案與影響範圍，**須使用者確認後才動**
- 只有互動元件（表單、圖表）由 JS 渲染而正文已在 HTML → 不觸發
- 不得以 user-agent 判斷對 bot 回傳不同內容——屬 cloaking（禁止動作）

---

## R12 — 索引提交與量測（Google + Bing）

**判準**：`web_surfaces` 非空，且下列任一不成立：

| 檢查 | 依據欄位 |
|---|---|
| Google Search Console 已驗證 | `pages[].site_verification` 含 `google`，或使用者確認已用 DNS 驗證 |
| Bing Webmaster Tools 已驗證 | `site_verification` 含 `bing`，或使用者確認已驗證 |
| sitemap 已存在且可提交 | `crawler_directives.sitemap_files` / `robots_txt_sitemaps` |
| 內容更新會主動通知 Bing | `metadata_apis.indexnow` |

**動作**：
- 未驗證 → 列入「需人工後續」：於 GSC 與 BWT 驗證並提交 sitemap；BWT 可直接匯入 GSC 設定
- 有建置／部署流程且未接 IndexNow → 規劃在部署後送出變更 URL 至 IndexNow（需使用者提供或同意產生 key，key 檔置於站台根目錄）。實作要求：key 檔在部署**前**產生並隨站台上線；每次只送 `lastmod` 與上次送出紀錄不同的 URL，不重送未變更頁面；回應 200／202 才記錄為已送出，其他狀態碼視為失敗並輸出回應內容（讀取上限 8 KiB）
- 量測指向一手報告：GSC 的 Generative AI performance report、BWT 的 AI Performance（Copilot、Bing AI 摘要與 select partner integrations；官方未點名 ChatGPT），以其 Citation Share／Intents／Topics（2026-06 preview，A9）判讀各 grounding query 的引用佔比；Topics Portfolio（2026-10-13 beta，A9）的 Opportunity Queries 只作規劃方向參考，官方標明非精確數據

**為何**：ChatGPT 與 Copilot 的檢索層是 Bing 索引（A9），只做 Google 等於放棄這兩個引擎。

**邊界**：
- 驗證碼由使用者從各自後台取得，**不得**填造 `content` 值
- 無部署流程者不為 IndexNow 新建 CI——列為建議，交由使用者決定
- 不引用第三方工具的「AI 可見度分數」作為成效依據（A1）

## R13 — AI 使用偏好宣告

**判準**：`web_surfaces` 非空，且 knowledge_anchors A12 中「可實作」欄為「是」或「需使用者決定政策」的機制尚未宣告；或已宣告的語法與 A12 最新狀態不符。

**動作**：
- 第一次執行時詢問使用者政策：是否允許 AI 訓練（`train-ai`／`ai-train`）、AI 即時輸入（`ai-input`／`ai-use`）、搜尋（`search`），寫入 config（`ai_usage`）；之後依 config 套用，不再詢問
- 依 A12 當下可實作的機制同時輸出，並存不衝突：
  - IETF aipref：robots.txt `Content-Usage: train-ai=y|n, ai-use=y|n, search=y|n`；HTTP header `Content-Usage`（靜態站用 `_headers` 的 `/*` 規則）
  - Cloudflare Content Signals：robots.txt `Content-signal: search=yes|no, ai-input=yes|no, ai-train=yes|no`
  - TDMRep：僅在使用者要表達 EU DSM 第 4 條保留時輸出 `/.well-known/tdmrep.json`
- 有建置流程者由建置產生，不手寫靜態檔

**邊界**：
- 政策值是內容授權決策，**不得**由 agent 代填預設值
- aipref 仍為 draft（A12），語法以 A-5 最新抓取為準；狀態變動時依 research_protocol A-5 判讀規則修正
- 不得宣稱這些宣告會提升排名或 AI 引用；它們只表達使用偏好，主要廠商官方頁截至 A12 驗證日皆未宣告支援
- 只追蹤不實作 A12 中「可實作＝否」或「網站端無需動作」的項目（Web Bot Auth、MCP Server Card、WebMCP、個人 draft）

---

## R14 — Favicon

**判準**：`web_surfaces` 非空，且頁面無 `<link rel="icon">`、`/favicon.ico` 亦不存在；或 favicon 非 1:1、小於 48x48，或僅提供 SVG。

**動作**：以作者／專案既有的 1:1 圖（先 `curl -sIL` 驗證 200 且為 image/*）轉成 PNG（建議 48 的倍數，如 192x192）放站台根目錄，每頁 `<head>` 加 `<link rel="icon" href="/favicon.png">`；有建置流程者由建置模板輸出。

**依據**：knowledge_anchors A2 favicon 支援格式（`developers.google.com/search/docs/appearance/favicon-in-search`，Last updated 2026-08-28：BMP、GIF、ICO、PNG、JPEG、PPM、TIFF，未列 SVG；1:1、至少 8x8，建議大於 48x48；每個 hostname 一個）。使用者 2026-10-03 指定納入規則。

**邊界**：
- 找不到可驗證的 1:1 圖 → 不得填造路徑，列為「需提供 favicon」待辦
- favicon 影響搜尋結果的站台圖示顯示，不是排序訊號，不得宣稱提升排名
- 子路徑站台（同 hostname 下多站）共用同一 favicon，不在子路徑另設

---

## R15 — 網址遷移與導向

**判準**（來源：`crawl_site.py` 的 `probes`、`legacy`）：

| 判準 | 嚴重度 |
|---|---|
| 不存在的路徑回 3xx（`probes.missing_page`），尤其導回首頁 | High |
| 不存在的路徑回 404，但頁面只有平台預設錯誤頁、沒有專案介紹與導覽 | Medium |
| 舊網址（git 歷史推出）回 302／307，或導回首頁（`to_root`） | High |
| 舊網址回 404，但現行站有語意對應的頁面 | Medium |
| `http://`、結尾斜線、`.html`、`index.html` 變體回 307／302 或多跳 | Low |

**動作**（每一項都列為「需使用者決策」，以 `AskUserQuestion` 逐網址確認後才套用）：
- 不存在的路徑回 404 頁（狀態碼 404）：頁面含專案介紹（一兩句定位）、首頁連結與文件導覽，`<meta name="robots" content="noindex">`；不兜底導向首頁
- 一頁拆成多頁：原網址以單一 301 導到其中一頁（承接原主題主體的那頁）
- 改名或併入其他頁：舊網址以單一 301 導到語意最接近的現行頁；整理成一張對照表放在部署設定（worker、`_redirects`、伺服器設定或其讀取的對照檔），由建置或部署讀取
- 已移除且沒有對應頁的網址：回 404 頁，不導回首頁
- 網址變體統一 301 到 canonical 形式

**為何**：Google 把「導回首頁」與「302 兜底」視為 soft 404，舊網址累積的訊號不會轉移；302／307 是暫時導向，Google 會繼續索引來源網址。

**邊界**：
- 對照表的對應關係須以頁面內容查證；拆分要導向哪一頁、哪些網址移除改回 404，一律由使用者決定，不自行套用（使用者 2026-10-23 指定）
- 不為了消除 404 而把網址導到不相干的頁面；沒有對應頁就讓它回 404 頁
- 導向由共用範本產生時，修範本而非逐站修補，並在規劃註明範本路徑
- Cloudflare 等平台自動加上的變體導向無法改碼時，列為 Low 並說明平台限制

---

## R16 — 索引範圍

**判準**：`crawl_site.py` 的 `composition` 中，單一非主要內容前綴（版本頁 `/released/*`、展示頁、標籤頁、分頁）占 sitemap URL ≥ 30%；或同一模板產生大量內容極少的頁面（`word_count` 低於站內中位數的 1/3）；或站台讓使用者產生供直接分享、協作或工具用途的頁面（分享連結頁、生成結果頁、互動工具輸出頁）且可被索引或列入 sitemap。

**動作**：列為「需使用者決策」，選項如下：

| 選項 | 做法 |
|---|---|
| 保留索引頁、單頁 noindex | 保留聚合頁（如 `/released/`）可索引，個別頁加 `<meta name="robots" content="noindex, follow">` 並移出 sitemap |
| 只移出 sitemap | 頁面仍可被連結發現，但不主動提交 |
| 維持現狀 | 該類頁面確實有人搜（例：版本號查詢承接得到），記錄理由 |

**為何**：sitemap 是提交「希望被索引的頁面」，大量低價值頁面會稀釋爬取資源與站點品質訊號（Google build-sitemap 文件：只放想出現在搜尋結果的正式網址）。使用者產生的分享／生成／工具頁，Google 建議預設以 noindex（robots meta 或 `X-Robots-Tag`）或 robots.txt 阻擋，只索引為搜尋而做的內容（`developers.google.com/search/docs/monitor-debug/prevent-abuse`「Only index content meant for Search」，Last updated 2026-10-26）。

**邊界**：
- 未經使用者確認不加 noindex（禁止動作「未經確認即改動 noindex」）
- 不刪除頁面；本規則只決定索引與提交範圍

---

## 禁止動作（違反即刪除該建議，不保留）

| 反模式 | 為何禁止 |
|---|---|
| 關鍵字堆砌（title / description / 內文重複塞詞） | 直接觸發垃圾內容判定 |
| title／description 與頁面內容不符（為了熱度放入該頁沒講的詞、描述頁面上不存在的功能或資訊） | 誤導點擊屬垃圾內容訊號；Google 也會改寫與內容不符的 title link，熱度詞反而不會出現 |
| 為查詢變體大量產生近似頁面 | Google 明列為 scaled content abuse |
| 標註頁面上不存在的內容（假 FAQ、假評分、假作者） | 結構化資料垃圾，會被人工處分 |
| 隱藏文字、以 CSS 藏關鍵字、cloaking | 明確違規 |
| 宣稱 llms.txt 有 SEO／AI 可見度效果 | 與官方立場衝突（A3） |
| 承諾排名或流量成長幅度 | 無法驗證；研究數據只能標為研究結論 |
| 在 `code_type` 無 web surface 時虛構頁面優化 | 幻覺；該類專案的 surface 是 R8–R10 |
| 大量頁面套用同一份樣板 description / OG | 重複內容訊號，且對使用者無資訊價值 |
| 未經確認即改動 `noindex`、robots.txt 封鎖規則、遠端 repo metadata | 這些是有意的營運決策，誤改後果外顯 |
| 內容未實質變動卻更新 `dateModified` / 可見日期 | 操弄新鮮度訊號；Google 要求日期反映實際更新（A10），spam policies 已涵蓋 AI 回答（A1） |
| 以「GEO 技巧」改寫既有內容（塞統計、塞引言、改句式） | 綜述研究顯示無穩定跨平台因果效果，且可能損害檢索（A8） |
| 依 user-agent 對 AI bot 回傳不同內容 | cloaking |

---

## 嚴重度定義

| 級別 | 判準 |
|---|---|
| **Critical** | 導致頁面無法被索引或無法被引用（全站 Disallow、誤設 noindex、封鎖檢索型 bot、canonical 指向錯誤頁、主要內容僅存在於 CSR） |
| **High** | 主要頁面缺 title / description / h1，結構化資料解析失敗，或多語站缺 hreflang |
| **Medium** | 缺 sitemap、缺 OG、標題階層混亂、套件登錄頁 metadata 空白、未驗證 GSC / BWT、內容頁缺 `dateModified` |
| **Low** | 長度超標、實體名稱寫法不一致、缺 `Sitemap:` 指令 |
