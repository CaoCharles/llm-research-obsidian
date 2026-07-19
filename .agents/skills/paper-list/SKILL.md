---
name: paper-list
description: 列出今日相關度最高的 arXiv 論文
argument-hint: "[top_n] [date]"
---

# /paper-list - 列出相關論文

列出當天相關度最高的論文（僅篩選，不進行 AI 分析）。

## 參數

- `$ARGUMENTS[0]` - Top N（可選，預設 10）
- `$ARGUMENTS[1]` - 日期（可選，預設今天，格式：YYYY-MM-DD）

## 範例

```
/paper-list         # 列出今天 Top 10
/paper-list 20      # 列出今天 Top 20
/paper-list 10 2025-02-03  # 列出指定日期 Top 10
```

## 執行步驟

1. 解析參數：
   - Top N: `$ARGUMENTS[0]` 或預設 10
   - 日期: `$ARGUMENTS[1]` 或預設今天

2. **嘗試 CLI 抓取**（優先）：

```bash
cd lpdd && uv run python cli.py list --top {top_n} [--date {date}]
```

3. **若 CLI 因 proxy/網路問題失敗，改用 WebSearch 備援**：

   使用 WebSearch 工具搜尋最新論文，搜尋策略：
   - 搜尋關鍵字組合：`arxiv {date_month} LLM evaluation safety alignment jailbreak benchmark red team`
   - 可加上 `site:arxiv.org` 限定來源
   - 根據使用者的研究領域（LLM 評測、安全、對齊）篩選相關論文
   - 對搜尋結果去重（檢查 Papers/ 目錄中已有的 arXiv ID）

4. 將結果以表格形式顯示給使用者：

| 排名 | 分數 | arXiv ID | 標題 |
|------|------|----------|------|
| 1 | {score} | {arxiv_id} | {title} |

5. 顯示論文總數統計

## 輸出格式

終端輸出：表格形式顯示論文列表
- 不寫入 Obsidian
- 不進行 AI 分析
