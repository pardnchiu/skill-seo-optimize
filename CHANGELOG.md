# Changelog

完整規範以 `SKILL.md` 與 `scripts/` 為準（＝最新規範）；本檔只用於快速定位先前執行本 skill 套用到專案的 SEO 變更（meta、JSON-LD、robots.txt、sitemap、`_headers`、llms.txt、建置腳本等）與最新規範的差異，命中即直接修改。

最新改動：2026-10-30

## 破壞性變更

- 作者 `same_as` 改讀 `{skill_dir}/.doc/author.json`；不存在時詢問一次寫入
- 本 skill 依專案特定契約寫入產生器的設定檔（如文件站的 SEO 設定 JSON）→ 不再寫入；改列「交由呼叫方」，由產生器 skill 依規劃套用
- title 尾綴為 ` - {name}`、`{owner}/{repo}` 或品牌前置（`owner/repo: …`）→ 改為 `{主題} | {品牌}`／`{主題}｜{品牌}`，不帶帳號前綴
- 使用者產生的分享連結頁、生成結果頁、互動工具輸出頁可被索引或列入 sitemap → 依 R16 列為需使用者決策（預設 noindex 或移出 sitemap；Google prevent-abuse 2026-10-26）
- title／description 含該頁內文沒涵蓋的關鍵字（為熱度放入），或描述頁面上不存在的內容 → 改回描述該頁實際內容；熱度詞移到真正涵蓋它的頁面或先補內容（R1、R2）
- 部署設定把 404 兜底導向首頁（例：worker `if (response.status !== 404) return response; return Response.redirect("/", 302)`）、或已刪頁面以 302／307 導回首頁 → 不存在路徑回含專案介紹的 404 頁（狀態碼 404），拆分頁的原網址 301 到其中一頁、移除的網址回 404 頁，逐網址經使用者同意後套用（R15）
- config `keyword_volume` 無 `terms` → Step 3.2 重量主要關鍵字並寫入 `terms`，供熱度下滑判斷
- 產出寫在 `{PROJECT_PATH}/.doc/seo-optimize/`（config.json、`research-{date}.md`、plan、applied）→ 搬到 `{skill_dir}/.doc/{網域}/`：`config.json`、`research/{date}.md`、`plan/{ts}.md`、`applied/{ts}.md`；專案內的 `.doc/seo-optimize/` 刪除（規則見 output_format.md「落檔規則」）

- 內容雜湊只算頁面原文、改 title／description／keywords／JSON-LD 不更新 `dateModified`／`lastmod` → 雜湊納入該頁 meta 與不含日期的 JSON-LD
- 有 web surface 但未產生 llms.txt（舊判準僅 agent-facing 文件）、或因頁數 ≤ 5／單一 surface 未建 sitemap、robots.txt → 依 R7 全部補上
- 既有頁面內文未點名競品，或競品少於 3 個、未依熱度選出 → 依 Phase B-4 重定競品（至少 3 個），在每個語言版本內文加入關聯／差異／特點段落
- 次要關鍵字含冷僻詞（avg、recent12w、recent4w 皆 < 1）→ 移除或換成較高熱度寫法並詢問，連帶重評 `one_liner` 與 topics
- en 關鍵字熱度以 `US` 量（config `keyword_volume.geo` 無 `WW`）→ 以 `--geo WW --hl en-US` 重量 en 詞並依結果重評、詢問，寫回 `keyword_volume.geo`
- title／meta description／H1 含競品名或「X alternative／X 替代」→ 改為本專案自身定位（高熱度類別詞與生態詞），競品名只留內文對比
- 關鍵字只依出現來源數選定、未量熱度（config 無 `keyword_volume`）→ 跑 Phase B-4／B-5 與 Step 3.2，依熱度 × 競品交集重選並詢問，寫入 `keyword_volume`、`competitors`
- 頁面範本或腳本於載入時以 history API／`location.hash` 移除 URL hash、強制捲回頂端，或主要內容預設收在折疊區／tab → 保留 hash、移除載入時的捲動控制、主要內容預設展開（R5，Google snippet「Read more」深層連結條件）
- 根路徑依 `Accept-Language`／IP 自動導向其他語言版 → 改為根路徑回傳固定內容並放可見語言切換連結（R3）
- 關鍵字僅由原始碼推導（config 無 `keyword_research`）→ 跑 Phase B 競品研究（搜尋第一頁、GitHub 高星同類、HN），依 Step 3「候選設計」重新提出關鍵字並詢問，寫入 `keyword_research`；關鍵字變動時連帶重評 `one_liner` 與 topics（R9）。舊 Phase B（關鍵字後補查）改名 Phase C
- README 首段只回報建議、repo description 另寫 → 依 R9 設計 config `one_liner`（en／zh），repo description 改為 `one_liner.en`（保留 `(module)` 等前綴），README 與中文 README 順序 3 那一行替換為 `one_liner`
- robots.txt `Content-Usage:` 與 `_headers` 的 `Content-Usage` header 缺 `ai-use=` → 依 config `ai_usage` 補成 `train-ai=y|n, ai-use=y|n, search=y|n`（R13）
- Person `sameAs` 未含 `{skill_dir}/.doc/author.json` 的 `same_as` 全部項目 → 補齊，作者網站本身也放入；舊規則「`sameAs` 不放節點自己的 `url`」已移除（R10）
- 以地區／職能／口號等定位文字宣告的 `Organization` 節點（作者掛 `founder`）→ 移除，改放可見署名或 tagline；多語頁改用各語言正式名稱並共用 `@id`（R6）
- `dateModified`／sitemap `lastmod` 取自檔案 mtime 或每次建置日期 → 改為內容雜湊變動才更新 `modified`，頁面可見日期、JSON-LD、`lastmod` 取同一值（R6 日期）
- llms.txt 連結指向 HTML 頁 → 改指向每頁 Markdown 版（`/{slug}.md`），並補齊 R7.3 v2 的探索連結、可見連結與 `.md`／`.txt` 的 `charset=utf-8`
- IndexNow 每次重送全部 URL 或未檢查回應碼 → 只送 `lastmod` 與上次送出紀錄不同的 URL，200／202 才記為已送出，key 檔於部署前產生（R12）
