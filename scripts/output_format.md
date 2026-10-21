# Output Format

兩份產出：**優化規劃**（Step 4，取得確認前）與**執行結果**（Step 6，套用後）。皆使用繁體中文，技術術語保留英文。

---

## 一、優化規劃 `{yyyy-MM-dd_HH-mm}-plan.md`

```markdown
# {project_name} SEO / AEO 優化規劃

## 目標設定

| 項目 | 值 |
|---|---|
| 主要關鍵字 | {primary_keywords} |
| 次要關鍵字 | {secondary_keywords} |
| 目標地區 / 語言 | {region} / {locale} |
| 目標引擎 | {engines} |
| 實體營業地點 | {有 / 無} |

## 專案盤點

| 項目 | 值 |
|---|---|
| code_type | {library / cli / web-app / static-site / docs-site} |
| web surface | {路徑與頁數；無則寫「無 web surface」} |
| 套件登錄 | {npm / pkg.go.dev / PyPI / Packagist / 無} |
| 正式網域 | {domain；未確認則寫「未確認」} |
| 研究依據 | `research-{yyyy-MM-dd}.md` |

## 優化方向

{2–4 句。說明本專案在目標關鍵字下的處境，以及為何選擇下列這組動作。
不寫通用 SEO 常識，只寫由本次分析與研究得出的判斷。}

## 待執行項目

依嚴重度排序。每項必須可對應 `optimization_rules.md` 的規則編號。

### Critical

#### C1. {標題}

- **規則**：{R7.1}
- **檔案**：`{path}`{:line}
- **現況**：{實際觀察到的內容，引用原文}
- **動作**：{具體要改成什麼}
- **依據**：{research digest 或 knowledge_anchors 的哪一條}

**變更預覽**：
\`\`\`diff
- {before}
+ {after}
\`\`\`

### High
...
### Medium
...
### Low
...

### 過時參數（最低優先）

依 Step 1 報告「過時參數」，目標仍在使用或可能被新增的過時項目。

| 參數 | 檔案 | 狀態 | 動作（移除／保留） | 依據 |
|---|---|---|---|---|

## 需使用者決策

| 項目 | 需確認什麼 | 未確認的影響 |
|---|---|---|
| {正式網域} | {canonical / sitemap 要用哪個網域} | {無法產生 canonical} |

## 不執行項目

{列出分析中出現、但依 optimization_rules.md 邊界條款判定為「不該做」的項目，附原因。
此段的作用是讓使用者知道哪些常見建議被刻意排除，例如：}

| 項目 | 不執行原因 |
|---|---|
| 產生 FAQ 頁 | 使用者未主動提及 |
```

---

## 二、執行結果 `{yyyy-MM-dd_HH-mm}-applied.md`

```markdown
# {project_name} SEO / AEO 優化執行結果

> 規劃：`{yyyy-MM-dd_HH-mm}-plan.md`

## 已套用

| # | 規則 | 檔案 | 變更 |
|---|---|---|---|
| C1 | R7.1 | `public/robots.txt` | 移除全站 Disallow |

## 未套用

| # | 規則 | 原因 |
|---|---|---|
| M3 | R4 | 找不到 OG 圖檔，需使用者提供 |

## 需人工後續

- [ ] {項目，例：R9 `gh repo edit --description "..."`（使用者於詢問時否決，未執行）}

## 驗證方式

{列出使用者可自行驗證的具體指令或 URL，例如：}

- `curl -s https://{domain}/robots.txt` 確認封鎖已移除
- Google Search Console → 網頁索引狀況，觀察 {N} 天後的變化
- Search Console 的 Generative AI 成效報告追蹤 AI 功能曝光
```

---

## 撰寫規則

1. **每項動作都要有錨點**——實際檔案路徑與現況原文。指不到檔案的建議刪除
2. **每項動作都要有依據**——指向本次 research digest 或 knowledge_anchors 的條目編號
3. **禁止推測性語言**——「未來可能」「建議考慮」「或許可以」出現即重寫或刪除
4. **零項目是合法輸出**——某嚴重度無項目時寫「無」，不硬湊
5. **不承諾成效**——可寫「研究顯示 X」並標註來源，不寫「可提升 N% 流量」
6. **量測方式要可執行**——寫得出指令或具體介面路徑，寫不出就不寫

## 落檔規則

- 目錄：`{PROJECT_PATH}/.doc/seo-optimize/`，不存在時建立
- 三種檔案：`research-{yyyy-MM-dd}.md`、`{yyyy-MM-dd_HH-mm}-plan.md`、`{yyyy-MM-dd_HH-mm}-applied.md`
- 設定：`{PROJECT_PATH}/.doc/seo-optimize/config.json`
- **永遠不在專案根目錄落檔**
- 寫入後提醒使用者確認 `.doc/` 是否需加入 `.gitignore`
