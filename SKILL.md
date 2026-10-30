---
name: seo-optimize
description: 分析專案並實際套用 SEO / AEO / GEO 優化。當使用者要求優化搜尋排名、提升 AI 引擎（AI Overviews / ChatGPT / Perplexity / Claude）引用機率、檢查 meta 標籤與結構化資料、處理 robots.txt、sitemap、hreflang 與 Bing / IndexNow 索引提交、或針對特定關鍵字與地區推廣專案時使用。每次執行都會重新查找近半年的 SEO / AEO 現況。
---

# SEO / AEO Optimizer

以**當次查得的近半年研究**為依據，分析專案實際暴露的搜尋面向，規劃並套用 SEO / AEO 優化。

## Command Syntax

```
/seo-optimize [PROJECT_PATH] [--plan] [--reset]
```

### Parameters (All Optional)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PROJECT_PATH` | 當前目錄 | 專案根目錄 |
| `--plan` | — | 只產出優化規劃，不修改任何檔案 |
| `--reset` | — | 清除 `{skill_dir}/.doc/{網域}/config.json`，重新詢問關鍵字 |

`{skill_dir}` 為本 `SKILL.md` 所在目錄的絕對路徑，依當前執行環境實際載入位置代入。

所有產出（研究、config、plan、applied）集中在 `{skill_dir}/.doc/`，依網域分資料夾，不寫入專案目錄；結構與 `{網域}` 解析見 [`scripts/output_format.md`](scripts/output_format.md)「落檔規則」。目標未指定子網域時只分析 apex 網域本身。

```bash
/seo-optimize                      # 完整流程：研究 → 分析 → 詢問 → 規劃 → 確認 → 套用
/seo-optimize --plan               # 只出規劃
/seo-optimize ./my-site --reset    # 指定專案並重設目標設定
```

### 呼叫方

其他流程可在產出後以專案根呼叫本 skill。檢查範圍由 Step 2 偵測決定，不由呼叫來源決定，所以每個入口都會檢查到同樣的面向：

| 偵測結果 | 必檢規則 |
|---|---|
| `git remote get-url origin` 為 `github.com` | R9：repo description、topics、homepage 與 README 簡短描述，不一致時以 `AskUserQuestion` 附完整 `gh repo edit` 指令詢問 |
| `web_surfaces` 非空 | R1–R7、R10–R16 頁面層與爬蟲指令 |
| `code_type` ∈ {library, cli} | R8 套件登錄頁、R10 |

呼叫方指明由它產生的檔案（例：建置來源、設定檔、頁面原始檔）本 skill 只檢查、不修改：修正項照常列入規劃並標「交由呼叫方」，由呼叫方依規劃套用。呼叫方或使用者給的站台決策（例：title 不列某類名稱、保留某檔、不設競品）寫入 config `decisions`。

**為何：** repo 頁與文件站是同一組定位的兩個搜尋面，只檢查呼叫來源負責的那一面，另一面的描述會漂移（例：README 產生後 repo description／topics 未檢查）。產生器管理的檔案被本 skill 直接改，下次產生就被覆蓋，或與產生器的事實來源分岔。

---

## Workflow

```
1. 研究   →  有 3 日內的 SEO／AEO／GEO 研究報告則沿用；沒有才跑 research_protocol.md Phase A 並存檔
2. 分析   →  讀 {網域}/ 最新的 plan／applied 取得上次結論；analyze_seo.py 盤點 surface；有部署網域則 crawl_site.py 爬線上站並測舊網址（git 歷史推出）；研究目標內容（使用者提及的目標，未提及則為本專案）：先讀 README／doc，不足再做全專案分析，產出 seed 詞與能力清單；對照 Step 1 報告找出目標缺少的新參數／資料
2.5 競品   →  research_protocol.md Phase B：找出最熱門的競品至少 3 個（B-1～B-3），收集競品用詞中英各 ≥ 10 個（B-4），逐詞量熱度：中文台灣、英文全球（B-5）
3. 設計   →  依「熱度 × 競品交集 × 原始碼能力」設計關鍵字候選與定位關聯，AskUserQuestion 確認；地區與引擎用固定預設
3.2 複查   →  定案詞重量熱度，附表 AskUserQuestion 篩選；通過者寫入 config.json
3.5 補研究 →  research_protocol.md Phase C，依在地性與專案類型補查
4. 規劃   →  產出 plan/{ts}.md，向使用者呈現並等待確認
5. 套用   →  確認後依 optimization_rules.md 修改檔案
6. 驗證   →  產出 applied/{ts}.md，列出已套用 / 未套用 / 需人工後續
```

`--plan` 時流程止於 Step 4。

---

## Step 1：研究（強制 gate，不可跳過）

**先檢查 `{skill_dir}/.doc/research/` 有無 3 日內生成的 SEO／AEO／GEO 研究報告**（檔名日期 ≥ `date -v-3d +%Y-%m-%d`，macOS；Linux 用 `date -d '3 days ago' +%Y-%m-%d`）：有則讀取最新一份沿用；沒有才完整跑一次 [`scripts/research_protocol.md`](scripts/research_protocol.md) 的 Phase A，結果存成 `{yyyy-MM-dd}.md`（skill 層，跨專案共用）。3 日沿用只適用這份報告；競品研究（Phase B）、補研究（Phase C）與熱度量測各依其步驟條件執行，不因此略過。

| 條件 | 行為 |
|---|---|
| 開始執行 | 先 `date +%Y-%m-%d` 取得今日，推算近半年時間窗 |
| 有 3 日內的報告 | 讀取最新一份沿用，略過 A-1／A-2／A-5 與 anchors 更新，向使用者說一行「沿用 {報告路徑}」 |
| 沒有 3 日內的報告 | 執行下列查詢並寫入報告 |
| 執行查詢 | Phase A-1 十二組查詢並行送出；Phase A-2 五個一手來源以 WebFetch 實抓；Phase A-5 標準與提案追蹤（IANA well-known 註冊表、IETF aipref／webbotauth、llmstxt.org、Cloudflare Content Signals、MCP Server Card）實抓並與 anchors A12 逐列比對 |
| 查得結果與 [`scripts/knowledge_anchors.md`](scripts/knowledge_anchors.md) 不符 | 以本次實抓的 Tier 1 來源為準，**就地更新 knowledge_anchors.md** 並改寫其「上次驗證日期」 |
| 網路不可用 | 明確告知使用者「本次未取得最新研究，以下依據為 {anchors 驗證日期} 的快照」，**不得靜默沿用** |
| A-5 查到狀態變動 | 依 research_protocol A-5 判讀規則更新 A12、optimization_rules；進入可實作門檻且適用本專案者列入規劃 |

**為何只快取 3 日：** SEO / AEO 有效做法半年內會反轉，必須定期重查；3 日內官方立場與標準狀態幾乎不會變，重查只浪費時間。2025 年主流指南建議加 llms.txt 提升 AI 可見度，2026-05 Google 官方文件表明其被忽略；同份文件亦推翻「特定 schema 觸發 AI 引用」。憑記憶作答會產出反效果的動作。

產出：Phase A 報告 `{skill_dir}/.doc/research/{yyyy-MM-dd}.md`；網域 digest `{skill_dir}/.doc/{網域}/research/{yyyy-MM-dd}.md` 記 Phase B／C 並連到該報告（格式見 research_protocol.md）。

**新規範回報（強制）：** 本次研究（含 A-5 標準追蹤）查到的內容只要**新於或高於 skill 現有資訊**——knowledge_anchors、optimization_rules、範本行為任一處沒有記載、記載過時或被推翻——回應的**最後一段**必須是「本次發現的新規範」表：

| 規範 | 來源 URL（日期） | skill 原本 | 最新內容 | 本次處理 |
|---|---|---|---|---|

「本次處理」寫實際改了哪個檔案（anchors／rules／範本與版號），或未處理的原因（例：仍為個人 draft、需使用者決定政策）。沒有新規範時寫一行「本次研究未發現高於 skill 現有資訊的新規範」。沿用既有報告時，表格內容取自報告的「本次發現的新規範」段，並註明沿用。

**為何：** 規範更新散在 digest 與 anchors 的修改裡，使用者不會逐檔比對；不在回應最後明列，就不知道 skill 這次被哪些新事實改寫、哪些還沒跟上。


---

## Step 2：分析專案

### 讀取過去分析

先列出 `{skill_dir}/.doc/{網域}/`，讀 `plan/` 與 `applied/` 各自檔名時間最新的一份；`analysis/` 有檔案時讀最新一份作為背景資料（skill 外部產生的數據分析，不當成上次 plan）；`research/` 只在 Step 2.5 判斷是否沿用時讀最新一份。

| 上次結論 | 本次處理 |
|---|---|
| applied 的「未套用」「需人工後續」、plan 的「需使用者決策」 | 逐項以本次實抓狀態重驗：已解決 → 規劃的「與上次分析的差異」記為已解決；仍存在 → 列入本次規劃並標「延續自 {ts}」 |
| 使用者否決或列入「不執行項目」 | 狀態沒變就不再提出；狀態有變才重提並說明變了什麼 |
| config `decisions` | 視為已定案：Step 3 不重問、Step 4 規劃不提出與其衝突的項目；本次研究推翻其依據時列入「需使用者決策」並附來源，不自行改寫 |
| 已套用項目 | 抽查仍在線上生效；被覆蓋或回退的列為缺口 |
| 資料夾不存在或沒有 plan | 首次分析，規劃的差異段寫「首次分析」 |
| config 的 `last_optimized` 距今 < 28 天 | 規劃盤點標「觀察期不足（N 天）」；上次套用項目只驗證是否仍生效，不以排名、曝光、點擊、AI 引用的變化判斷成效，也不因此提出回退或改寫 |
| `last_optimized` 距今 ≥ 28 天 | `analysis/` 或 GSC／GA4 數據以 `last_optimized` 為切點比較前後同長度區間，結論記入規劃的「與上次分析的差異」 |

**為何：** 不讀上次結論，每次都會從零重列同一批項目、重問使用者已經否決的決策，也看不出上次的待辦有沒有真的完成。距上次優化太短時，重新索引與 GSC 數據尚未反映改動，據此判斷成效會把未生效誤讀成無效而反覆改寫。

### 盤點

```bash
python3 {skill_dir}/scripts/analyze_seo.py {PROJECT_PATH}
```

輸出 JSON：`code_type`、`web_surfaces`、`web_framework`、`package_metadata`、`crawler_directives`、`metadata_apis`、`pages`、`contents`。

### 線上爬取（有部署網域時）

```bash
python3 -I {skill_dir}/scripts/crawl_site.py https://{host} [--legacy {舊網址清單檔}]
```

只爬該 host：sitemap 索引中其他 host 的 sitemap 只計數不爬（`foreign_hosts_in_sitemaps`）。輸出 `status_counts`、`composition`（sitemap 依路徑前綴的占比）、`probes`、`legacy` 與每頁 `<head>` 盤點。

| 欄位 | 判讀 |
|---|---|
| `probes.missing_page` | 不存在的路徑必須回 404／410；回 3xx（尤其 `to_root`）→ R15 |
| `probes.http_root`、`slash_variant`、`html_variant`、`index_html` | 應為單一 301；307／302 或多跳 → R15 |
| `legacy[]` | 舊網址回 302／307 或 `to_root` → R15 |
| `composition` | 單一非文件前綴（版本頁、展示頁、標籤頁）占比 ≥ 30% → R16 |
| `pages[]` 與 `analyze_seo.py` 的 `pages` 不一致 | 線上與原始碼漂移（例：建置未部署、worker 改寫），以線上為準列缺口並註明來源檔 |

**舊網址清單：** 由 git 歷史推出被刪除或改名的頁面原始檔，依專案的「原始檔 → URL」對應換算成網址寫入清單檔（放 `{網域}/analysis/legacy-{yyyy-MM-dd}.txt`）；呼叫方已提供當日清單檔就沿用。依專案路由規則換算，換算不出的列入規劃「未確認」而不猜。

**為何：** worker 改寫、CDN 自動導向與已刪頁面的處理只存在於線上；只掃原始碼看不到。曾有多個站台的舊網址全被 302 導回首頁，原始碼盤點卻完全正常。

**腳本只做機械盤點，不理解專案在做什麼。**接著研究目標內容：

| 研究目標 | 做法 |
|---|---|
| 使用者提及特定目標（產品、頁面、URL、子專案、功能） | 以該目標為研究對象：本地檔案依下列文件順序讀；URL 以 curl 取原始 HTML 與其連到的文件 |
| 未提及 | 以 `PROJECT_PATH` 整個專案為研究對象 |

| 文件狀況 | 做法 |
|---|---|
| 有 README／`doc/`，且足以回答下表每一項 | 以文件為準，抽查入口檔確認文件未過時 |
| 沒有文件，或缺任一項的細節 | 做全專案分析：實讀入口檔、主要型別與匯出函式，提煉 3–5 個原始碼可查證的特色 |

據此判斷：

| 判斷項 | 用途 |
|---|---|
| 這個專案解決什麼問題、屬於哪一類工具 | Step 2.5 的 seed 詞（每語言 2–4 個，用使用者描述問題或找工具的說法，不用專案名） |
| 專案實際具備哪些能力 | Step 3 篩選候選：競品常用但本專案沒有的能力不得成為關鍵字 |
| 目標使用者是誰（開發者／終端使用者／企業） | 決定 R6 的 schema 類型 |
| 有無實際部署網域 | 決定 canonical / sitemap 能否產生 |
| README 是否由產生器管理（呼叫方指明，或專案 CLAUDE.md 標示） | 決定 R9 是直接改寫還是只回報建議 |
| `git remote get-url origin` 是否為 `github.com` | 是 → R9 必檢，不論 `code_type`；以 `gh repo view {owner}/{repo} --json description,repositoryTopics,homepageUrl` 取現況 |

**對照 Step 1 報告找缺口：** 逐條取報告的「本次可執行結論」與「本次發現的新規範」中的參數與資料（meta、schema 屬性、HTTP header、robots／well-known 指令、檔案如 llms.txt 新欄位等），以 `analyze_seo.py` 輸出與實際檔案檢查目標是否具備。

| 檢查結果 | 處理 |
|---|---|
| 目標已具備且值正確 | 不列 |
| 缺少、或語法／值落後報告 | 記為缺口，Step 4 列入規劃並標對應規則編號 |
| 報告有、`optimization_rules.md` 尚無對應規則 | 標「新規範」附報告來源 URL，Step 4 列入規劃 |
| 不適用目標（例：無 web surface 卻是頁面層參數） | 不列，規劃「不執行項目」寫原因 |

**為何：** 報告只說明市場上有什麼新要求，不會自己落到專案；不逐條對照，新參數只會停在報告裡。

**禁止**在 `web_surfaces` 為空時虛構頁面優化——該類專案的 surface 是套件登錄頁與 GitHub（規則 R8–R10）。

---

## Step 2.5：競品研究

以 Step 2 的 seed 詞跑 [`scripts/research_protocol.md`](scripts/research_protocol.md) 的 Phase B（B-1～B-5），結果寫入同一份 research digest 的「競品研究」段。競品至少 3 個，依熱度由高到低取：使用者點名者全部納入，不足 3 個時依 B-4「確定競品清單」以熱度排序補滿。

| 條件 | 行為 |
|---|---|
| config 無 `keyword_research`、帶 `--reset`，或 config 缺失 | 執行 Phase B，進入 Step 3 重新設計關鍵字 |
| `keyword_research` 距今 ≥ 90 天 | 執行 Phase B，Step 3 重新設計並詢問；既有關鍵字列為候選之一一起比較 |
| 未滿 90 天：以 `keyword_volume.anchor` 重量主要關鍵字，任一詞 `recent4w` < 記錄值的 50% | 執行 Phase B 並在詢問時列出下滑的詞與前後數值 |
| 未滿 90 天且熱度未下滑，未帶 `--reset` | 略過 Phase B，Step 3 沿用 config 關鍵字 |

**為何：** 只從原始碼推關鍵字，得到的是作者自己的說法；使用者實際搜尋、高星同類 repo 與社群熱門文章用的詞才是搜尋面上會被比對的詞。競品的品牌名與類別詞十之八九是熱門詞，不量熱度就會選到「沒人佔、也沒人搜」的詞（例：某本地 AI agent 首輪主詞 `local ai agent`、`24/7 personal ai agent` 熱度 ≤ 1，同期 `claude code` 36、`ollama` 12）。

---

## Step 3：設計關鍵字

先檢查 `{skill_dir}/.doc/{網域}/config.json`：

| 狀態 | 行為 |
|---|---|
| 存在、欄位完整、有 `keyword_research`，未帶 `--reset` | 載入並**向使用者複述一行**目前設定，繼續 Step 3.5 |
| 缺失、欄位不完整、無 `keyword_research`，或帶 `--reset` | 依下方「候選設計」產出候選，以 `AskUserQuestion` 詢問；既有欄位（`domain`、`ai_usage` 等）保留不重問 |

### 候選設計

| 條件 | 規則 |
|---|---|
| 成為候選 | 同時成立：(1) 原始碼確實具備該能力；(2) 該詞或其同義寫法在 Phase B 至少 2 個來源出現（第一頁 title／description、高星 repo description／topics、HN 標題、B-4 競品用詞）；(3) B-5 有熱度數據 |
| 排序 | 熱度高且與競品交集（競品品牌名、競品類別詞、本專案也支援的生態詞）者優先 |
| 冷僻詞 | 該語言量測 avg、recent12w、recent4w 皆 < 1（同次 anchor 換算）→ 不採用，主要、次要都不列；沒人搜的詞對行銷無意義 |
| 競品常用、本專案不具備 | 不列候選，列入規劃「不執行項目」並附原因（過度宣稱會被選去回答專案答不了的查詢） |
| 本專案獨有、競品未出現 | 有熱度者只能列為次要關鍵字並標「無競品交集」；冷僻者不採用 |
| 多語言 | 每個語言以該語言 Phase B 的結果各自設計，禁止由另一語言翻譯 |
| 詢問呈現 | 每個候選附證據：出現來源數、代表來源（repo 星數／HN points／第一頁排名） |
| topics 候選 | 取自 Phase B 收集到的高星 repo topics，再依 R9 門檻篩選 |
| 跨網域重疊 | 掃 `{skill_dir}/.doc/*/config.json`：候選詞已是其他網域的 `primary_keywords` → 詢問時標「與 {網域} 重疊」，由使用者選擇：本網域改用區分詞、保留重疊（例：前身專案）、或調整另一網域 |

### 與競品建立關聯

每個競品都要在每個語言版本的內文點名，寫出關聯、差異與本專案特點，並帶入競品品牌名與類別詞增加查詢觸發；依 B-4 的同型／異型決定說法：

| 競品類型 | 說法 | 例（本專案為本地 AI agent） |
|---|---|---|
| 異型（部署型態相反） | 點名競品，對比型態差異 | 競品 A、B 跑在廠商雲端 → 本專案跑在你自己的電腦，本地優先 |
| 同型 | 點名競品，講本專案可查證的特色 | 競品 C、D 是 TypeScript／Python 專案 → 本專案核心是單一 Go 執行檔、會自建工具 |
| 本專案支援的生態詞 | 直接當能力詞使用 | Claude Code、Ollama、MCP |

| 邊界 | 規則 | 為何 |
|---|---|---|
| 放置位置 | 競品名只放內文段落；title、meta description、H1、首頁開頭只寫本專案自身定位（可用高熱度的類別詞與生態詞） | 產品 title 蹭別人名稱顯得低端，使用者 2026-10-21 明確否決 |
| 不寫「替代品」 | 不用「X alternative」「X 替代」框定自己 | 把自己定位成別人的附屬；且 `X alternative` 類詞實測熱度多為 0 |
| 對比必須可查證 | 競品特性取自其官方頁或 `gh api`，本專案特性取自原始碼；不得暗示競品缺少它其實有的能力，也不得宣稱本專案不需要它實際依賴的東西 | 例：競品也能自建工具卻被寫成本專案獨有；本專案的沙箱工具依賴 Node.js／Python，卻寫「不用裝 Node.js 或 Python」屬誤導 |
| 只承接本專案答得了的意圖 | 競品的衍生詞（`{競品} 教學`、`{競品} install`、`{競品} pricing`）不列入關鍵字 | 本專案沒有別人專案的教學，放了等於宣稱答不了的查詢 |
| 放進既有內文 | 對比寫進首頁介紹段或概覽頁的既有段落；比較頁、FAQ 頁只在使用者主動提及時才做；無 `web_surfaces` 時列為規劃建議，README 由產生器管理時只回報 | 使用者 2026-10-21 否決比較頁與 FAQ；R5 也禁止為 AI 塞問答樣板 |

### 已固定的預設（**不再詢問**）

下列兩項由使用者於 2026-08-16 定案，適用所有專案。直接寫入 config.json，**禁止再以 AskUserQuestion 詢問**。

| 項目 | 固定值 | 意涵 |
|---|---|---|
| 地區 / 語言 | **每個語言版本各自完整優化，語言間等權** | `zh` 頁面全繁中、`en` 頁面全英文，日後新增任何語言同理。無「主語言／次語言」之分，`x-default` 不偏向任一語言。每個語言版本的 title / description / JSON-LD / og:locale 都要用該語言自身撰寫，禁止跨語言共用同一句。關鍵字研究與熱度：`en` 用英文量全球、`zh` 用台灣繁中量台灣 |
| 目標引擎 | **全部**：Google 一般搜尋、Google AI Overviews·AI Mode、ChatGPT、Perplexity、Claude | 因涵蓋 ChatGPT（OAI-SearchBot 為 HTML-only parser，見 A6），**「主要內容必須存在於初始 HTML」永遠是最高優先項**；CSR-only 站台一律列 Critical |

### 詢問內容（一次問完）

| # | Header | 問題 | 選項來源 |
|---|---|---|---|
| 1 | 關鍵字 | 想推廣的主要關鍵字（可複選 / 自填） | **依上方「候選設計」產出 3–4 個候選**，使用者可改用 Other 自填 |
| 2 | 在地性 | 有無實體營業地點 | 有（觸發 LocalBusiness schema 與 GBP 建議）／純線上 |
| 3 | AI 使用 | 是否允許 AI 訓練、AI 即時輸入、搜尋使用本站內容（R13；config 無 `ai_usage` 時才問） | 各類別允許／不允許／不表態 |

候選要是使用者會輸入搜尋框的詞，不是內部術語；不得從專案名硬湊。每個候選附 B-5 熱度（avg／recent12w／recent4w）與競品交集。

### Step 3.2：熱度複查（定案後，寫入 config 前）

使用者選定關鍵字、或規劃中寫好 title／description 後，把**實際要放進 title／description／H1 的詞組**（不是概念）用 `trends.py` 重量一次，附表以 `AskUserQuestion` 請使用者篩選；使用者通過後才寫入 config 與規劃。

| 條件 | 行為 |
|---|---|
| 詞組熱度明顯低於同概念的其他寫法 | 列出較高的寫法並建議替換（例：`local ai agent` 1.0 → `local ai` 14.2） |
| 落入冷僻門檻 | 標「冷僻」，改用較高熱度寫法或移除，不降為次要詞 |
| 使用者在後續對話改動關鍵字 | 對新詞重跑本步驟，不沿用舊量測 |
| `trends.py` 量不到 | 回報哪些詞未量、原因，詢問是否仍採用 |
| 詞組不是該頁內文實際涵蓋的主題 | 不放進該頁 title／description，不論熱度多高；改放到真正涵蓋它的頁面，或列為「需補內容」由使用者決定（R1、R2） |

詢問呈現：一張表列「詞｜各 geo avg／recent12w／recent4w｜放置位置（title／description／H1／內文）｜建議（保留／替換／降級）」，選項為「照建議」「全部保留」與 Other。通過的主要關鍵字連同量測值寫入 `keyword_volume.terms`。

**為何：** 概念上量過不代表最後寫進 title 的詞組有量；不重量就會把低量詞組寫進最重要的位置。篩選屬定位決策，由使用者拍板。

### config.json

```json
{
  "primary_keywords": ["go scheduler", "golang cron library"],
  "secondary_keywords": ["task scheduling", "fsnotify hot reload"],
  "locales": ["en", "zh-Hant"],
  "locale_policy": "per-language-full",
  "engines": ["google", "google-ai", "chatgpt", "perplexity", "claude"],
  "has_physical_location": false,
  "domain": "https://example.com",
  "keyword_research": "2026-10-06",
  "last_analyzed": "2026-10-21",
  "last_optimized": "2026-10-07",
  "keyword_volume": {"checked": "2026-10-06", "anchor": "golang", "geo": ["WW", "TW"], "terms": {"go scheduler": {"geo": "WW", "avg": 3.1, "recent12w": 3.4, "recent4w": 3.0}}},
  "competitors": [{"name": "robfig/cron", "type": "same"}],
  "decisions": [{"item": "title", "value": "只寫姓名與身分定位，不列專案名稱", "since": "2026-10-27"}],
  "one_liner": {
    "en": "A Go task scheduler with cron syntax, dependency chains, and fsnotify hot reload",
    "zh": "Go 任務排程器，支援 cron 語法、任務相依鏈與 fsnotify 熱重載"
  }
}
```

`one_liner` 由 Step 4 依 R9 設計，是 README 簡短描述、GitHub repo description 與 topics 的單一來源。

`keyword_research` 為關鍵字依 Phase B 競品研究設計的日期，對應 digest 檔名；要重新研究時帶 `--reset`。`keyword_volume` 記 Step 3.2 複查的日期、anchor、geo 與每個主要關鍵字的量測值（`terms`，供 Step 2.5 判斷熱度下滑）；`competitors` 記 B-4 的競品與同型（`same`）／異型（`opposite`）。

`last_analyzed` 為最新一份 plan 的日期，Step 4 產出 plan 時更新；`last_optimized` 為最新一份「已套用」非「無」的 applied 日期，Step 6 產出 applied 時更新，零套用不更新。兩者供 Step 2 判斷觀察期與跨網域 review。

`decisions` 記使用者或呼叫方定案的站台決策（`item`、`value`、`since`），只在使用者或呼叫方指示時新增、修改或移除。

`locales` 依專案實際存在的語言版本填寫；`locale_policy` 與 `engines` 為固定值，不因專案而異。

`domain` 依 output_format.md「落檔規則」的網域來源推得；有 `web_surfaces` 卻推不出時**問使用者**，不得填入佔位網域。無 `web_surfaces` 的套件不填 `domain`，資料夾用 `github-com-{owner}-{repo}`，不問。

---

## Step 3.5：補研究

依 Step 3 的答案跑 [`scripts/research_protocol.md`](scripts/research_protocol.md) 的 Phase C，結果併入同一份 research digest。

---

## Step 4：規劃

讀 [`CHANGELOG.md`](CHANGELOG.md) 定位差異：「破壞性變更」全部項目逐項比對專案中先前由本 skill 套用的產物，命中項直接列為規劃項目並於 Step 5 修改；回應中列出命中項與改動。

依 Step 1 報告補缺與汰舊：

| 來源 | 處理 |
|---|---|
| Step 2 找到的缺口（新參數／資料） | 列入規劃補上，依嚴重度排序 |
| 報告「過時參數」中狀態為已廢棄／被忽略，且目標仍在使用 | 列為移除項 |
| 報告「過時參數」中狀態為不再著重（例：`<meta name="keywords">` 已不被 Google 採用） | 不新增；既有者保留，相關項目排在規劃最後 |
| 過時參數相關的所有項目 | 一律放規劃「過時參數」段（Low 之後），不佔 Critical–Low |

**為何：** 規劃的順序就是動手的順序；過時參數投入再多也不影響結果，放前面只會排擠真正有效的項目。

再依 [`scripts/optimization_rules.md`](scripts/optimization_rules.md) 逐條比對分析結果，產出 `{skill_dir}/.doc/{網域}/plan/{yyyy-MM-dd_HH-mm}.md`（格式見 [`scripts/output_format.md`](scripts/output_format.md)），並把 config 的 `last_analyzed` 更新為本次日期。

**產出後必須向使用者呈現摘要並取得明確確認才進入 Step 5。**規劃會修改專案檔案，屬不易還原的動作。

`--plan` 模式在此停止。

---

## Step 5：套用

僅套用 Step 4 規劃中**已列出且使用者未否決**的項目。

| 界線 | 規則 |
|---|---|
| 檔案修改 | 逐項套用，每項對應規劃中的編號 |
| `robots.txt` 封鎖規則、`noindex` 移除 | 規劃中已標為「需使用者決策」者，未獲答覆前不動 |
| 遠端 repo metadata（`gh repo edit`） | 依 R9 比對現況，不一致時以 `AskUserQuestion` 附完整指令詢問；同意才執行並以 `gh repo view` 驗證，否決則列入需人工後續 |
| README | 由產生器管理時只回報建議，不直接改寫結構 |
| 建置產物（HTML、sitemap、robots.txt、llms.txt 等由建置產生者） | 不直接改；改產生它的來源後重跑建置 |
| 呼叫方或專案 CLAUDE.md 標示由產生器管理的檔案 | 不改；列入 applied「交由呼叫方」，附規則編號與建議值 |
| git | **不執行 `git commit` / `git push` / `git tag`** |

規劃外的「順手改一下」一律不做。

---

## Step 6：驗證

產出 `{skill_dir}/.doc/{網域}/applied/{yyyy-MM-dd_HH-mm}.md`，並執行下列自我檢查：

- [ ] Step 1 研究報告為 3 日內生成（本次執行或沿用）且含實抓的 Tier 1 來源；網域 digest 已落檔並連到該報告
- [ ] 已讀 `{網域}/` 最新的 plan／applied，上次的未套用、需人工後續、需使用者決策項目都已重驗，並記在規劃的「與上次分析的差異」
- [ ] 規劃沒有與 config `decisions` 衝突的項目；依據被推翻者已列「需使用者決策」
- [ ] config 的 `last_analyzed` 為本次 plan 日期；本次「已套用」非「無」時 `last_optimized` 為本次日期，否則維持原值
- [ ] 所有產出都在 `{skill_dir}/.doc/{網域}/`，專案目錄內沒有新增 `.doc/seo-optimize/`
- [ ] 有部署網域者已跑 `crawl_site.py`：`probes` 與 `legacy` 的 3xx／`to_root` 已列入 R15，`composition` 超過門檻者已列入 R16；舊網址清單由 git 歷史推出（推不出者標未確認）
- [ ] 關鍵字研究未逾 90 天、主要關鍵字熱度未下滑；否則已重跑 Phase B；跨網域重疊已標示並由使用者決定
- [ ] 研究對象為使用者提及的目標（未提及則為本專案）；文件不足時已做全專案分析
- [ ] Step 1 報告的可執行結論與新規範已逐條對照目標，缺口皆已列入規劃或「不執行項目」
- [ ] 報告「過時參數」已逐條比對，目標中的過時項目已列為移除或排在規劃「過時參數」段
- [ ] 競品至少 3 個且依熱度選出；B-4 中英各 ≥ 10 詞且逐詞有熱度（中文台灣、英文全球）
- [ ] 本次設計的關鍵字每個都能指到 digest「競品研究」的詞彙彙整列（≥ 2 來源且專案具備該能力），無冷僻詞，config 已寫入 `keyword_research`
- [ ] B-4 競品用詞與 B-5 熱度已落 digest；放進 title／description／H1 的詞組已經 Step 3.2 重量並經使用者篩選，config 已寫入 `keyword_volume`
- [ ] 本次改過的每個 title／description，主題詞與陳述都能在該頁 h1 或可見正文找到對應；沒有為了熱度放入該頁沒講的詞（R1、R2）
- [ ] title、meta description、H1、首頁開頭不含競品名；每個競品在每個語言版本內文皆有點名，且符合「與競品建立關聯」邊界（可查證、無替代品框定、無競品衍生詞、未擅自新增比較頁或 FAQ 頁）
- [ ] knowledge_anchors.md 與本次研究一致（不一致者已更新）
- [ ] 每項套用的變更都能指到 `optimization_rules.md` 的規則編號
- [ ] 每項變更都有實際檔案錨點，無虛構路徑
- [ ] 無「禁止動作」表中的任何一項（關鍵字堆砌、假 schema 等）
- [ ] `web_surfaces` 為空時未產生任何頁面層變更
- [ ] canonical / sitemap 中的網域為實際確認過的網域
- [ ] Organization 節點只代表實際存在的組織（定位文字不得成為 Organization），多語頁各用自身語言的正式名稱，`@id` 與作者網站一致
- [ ] Person `sameAs` 包含 `{skill_dir}/.doc/author.json` 的 `same_as` 每一項，個人與組織帳號分開，與作者網站差異已列入人工後續
- [ ] `dateModified` 由內容雜湊判定（含 meta 與 JSON-LD，本次改過的頁面日期皆已更新），連續建置兩次日期不變；頁面可見日期與 JSON-LD、sitemap `lastmod` 一致
- [ ] 接了 IndexNow 者：key 檔線上回 200，送出回 200／202，重跑只送有變動的 URL
- [ ] `csr_shell == true` 的頁面已列為 R11 Critical，未被其他內容層項目蓋過
- [ ] 目標引擎含 ChatGPT 時，R12 的 Bing Webmaster Tools 驗證狀態已檢查
- [ ] 驗證碼、IndexNow key 未被填造
- [ ] 未執行 git 寫入指令；`gh repo edit` 只在使用者於 `AskUserQuestion` 同意後執行，且已以 `gh repo view` 確認生效
- [ ] A-5 標準追蹤已實抓，A12 已更新驗證日期
- [ ] 未直接修改建置產物；呼叫方管理的檔案未修改，修正項已列「交由呼叫方」
- [ ] `web_surfaces` 非空者已產生 llms.txt：每頁有 Markdown 版與兩個探索連結、可見的 llms.txt／Markdown 連結；`.md`／`.txt` 回應帶 `charset=utf-8`
- [ ] 回應最後一段為「本次發現的新規範」表（或一行聲明無新規範）
- [ ] `CHANGELOG.md`「破壞性變更」已逐項比對既有產物，命中項已修改並列於回應；本次改了 `SKILL.md`／`scripts/` 者已更新 CHANGELOG

---

## CHANGELOG 維護

修改本 skill 的 `SKILL.md`／`scripts/`（含 Step 1 研究就地更新 anchors、rules）時，同一次改動內：

1. 更新 `CHANGELOG.md` 的「最新改動」日期
2. 本次含移除行為或需既有產物端處理的變更 → 寫進「破壞性變更」（一項一行、新者在上，寫清楚「既有產物中找什麼 → 改成什麼」）；新增與修正不記錄。CHANGELOG 不寫版號

**為何：** 讀完整規範（本檔＋`scripts/`）即得最新規範；CHANGELOG 只負責快速定位既有產物與最新規範的差異。只記破壞性變更，檔案不隨改動無限增長，落後多次的專案也能一次看完必須處理的項目；新增與修正在重跑時讀全規範自然取得。

---

## Reference Documents

| 階段 | 參考檔 | 用途 |
|---|---|---|
| Step 1 / 2.5 / 3.5 | [`scripts/research_protocol.md`](scripts/research_protocol.md) | 強制研究協定：查詢集、來源分級、衝突裁決、digest 格式 |
| Step 2 | [`scripts/analyze_seo.py`](scripts/analyze_seo.py) | 本地原始碼盤點 |
| Step 2 | [`scripts/crawl_site.py`](scripts/crawl_site.py) | 線上單一 host 爬取：sitemap、導向、`<head>`、404／導向探測、舊網址 |
| Step 2.5 / 3.2 | [`scripts/trends.py`](scripts/trends.py) | Google Trends 相對熱度，跨批次以同一 anchor 換算；輸出 avg、recent12w 與 recent4w |
| Step 1 / 4 | [`scripts/knowledge_anchors.md`](scripts/knowledge_anchors.md) | 已驗證的一手立場快照，用於偵測變動與識破業界迷思；每次執行後更新 |
| Step 4 / 5 | [`scripts/optimization_rules.md`](scripts/optimization_rules.md) | 規則 R1–R16、禁止動作、嚴重度定義 |
| Step 4 / 6 | [`scripts/output_format.md`](scripts/output_format.md) | 規劃與執行結果的報告範本 |
| Step 4 | [`CHANGELOG.md`](CHANGELOG.md) | 破壞性變更清單，快速定位既有產物與最新規範的差異 |
