---
name: paper-export
description: 匯出 LLM 評測論文清單為 Excel 檔案
argument-hint: "[date_spec] [keyword]"
---

# /paper-export - 匯出論文 Excel 清單

從 arXiv 即時抓取 LLM 評測相關論文，篩選後匯出為 Excel 檔案。

## 參數

- `$ARGUMENTS[0]` - 日期規格（可選，預設最近 1 天）
- `$ARGUMENTS[1]` - 額外搜尋關鍵字（可選）

### 日期規格支援格式

| 格式 | 說明 | 範例 |
|------|------|------|
| `YYYY-MM-DD` | 單日 | `2026-02-05` |
| `YYYY-MM-DD:YYYY-MM-DD` | 日期範圍 | `2026-02-01:2026-02-05` |
| `Nd` / `Ndays` | 最近 N 天 | `7d`, `30days` |
| `Nm` / `Nmonths` | 最近 N 個月 | `1m`, `3months` |
| `Ny` / `Nyear` | 最近 N 年 | `1y` |
| `YYYY` | 指定整年 | `2026` |

## 範例

```
/paper-export                          # 匯出最近 1 天的論文
/paper-export 7d                       # 匯出最近 7 天
/paper-export 1m                       # 匯出最近 1 個月
/paper-export 3m                       # 匯出最近 3 個月
/paper-export 6m                       # 匯出最近 6 個月
/paper-export 2026-02-01:2026-02-05    # 匯出指定日期範圍
/paper-export 1m "red team"            # 最近 1 個月的紅隊演練相關論文
/paper-export 3m "jailbreak"           # 最近 3 個月的越獄攻擊論文
/paper-export 2026 "prompt injection"  # 2026 年的提示注入論文
/paper-export 7d "RAG evaluation"      # 最近 7 天的 RAG 評測論文
```

## 執行步驟

### Step 1: 解析參數

- 日期規格: `$ARGUMENTS[0]` 或預設 `1d`（最近 1 天）
- 額外關鍵字: `$ARGUMENTS[1]`（可選）

若使用者用自然語言描述需求，先解析成對應參數：
- 「最近一個月的紅隊演練論文」→ 日期: `1m`, 關鍵字: `red team`
- 「2026 年的 jailbreak 論文」→ 日期: `2026`, 關鍵字: `jailbreak`
- 「近三個月的 RAG 評測」→ 日期: `3m`, 關鍵字: `RAG evaluation`

### Step 2: 執行 CLI 匯出

```bash
cd lpdd && uv run python cli.py export --date "{date_spec}" [--keyword "{keyword}"]
```

### Step 3: 回報結果

顯示匯出統計：
```
📊 Excel 匯出完成！

日期範圍：{start_date} ~ {end_date}
關鍵字：{keyword}（若有）
論文數量：{count} 篇
輸出路徑：{output_path}
```

### Step 4: 提供後續操作選項

```
想要進一步操作嗎？
- 輸入論文 arXiv ID 可以執行詳細分析：/paper-analyze {arxiv_id}
- 更換日期範圍或關鍵字重新匯出
```

## Excel 欄位說明

| 欄位 | 說明 |
|------|------|
| No. | 序號 |
| arXiv ID | arXiv 編號 |
| 論文標題 | 原始英文標題 |
| 作者 | 前 5 位作者 |
| 發表日期 | YYYY-MM-DD |
| 分類 | arXiv 分類（如 cs.CL, cs.AI） |
| 匹配關鍵字 | 匹配到的 LLM 評測相關關鍵字 |
| 匹配分數 | 關鍵字權重加總分數 |
| 摘要 | 英文摘要（前 500 字） |
| arXiv 連結 | 可點擊的 arXiv 頁面連結 |
| PDF 連結 | 可點擊的 PDF 下載連結 |

## 輸出

- Excel 檔案預設存放於 `Exports/` 目錄
- 檔名格式：`llm-papers-{date}.xlsx` 或 `llm-papers-{start}_to_{end}.xlsx`
- 包含表頭樣式、自動篩選、凍結窗格等功能

## 注意事項

- arXiv API 抓取量受限，超長日期範圍（如 1 年）可能無法取得所有論文
- 預設使用 `keywords.yaml` 中定義的 LLM 評測關鍵字進行篩選
- 若指定額外關鍵字，會改用該關鍵字搜尋（不套用最低分數門檻）
