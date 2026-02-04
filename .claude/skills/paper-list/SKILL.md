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

2. 執行 CLI 抓取並篩選論文：

```bash
cd lpdd && uv run python cli.py list --top {top_n} [--date {date}]
```

3. 將結果以表格形式顯示給使用者：

| 排名 | 分數 | arXiv ID | 標題 |
|------|------|----------|------|
| 1 | {score} | {arxiv_id} | {title} |

4. 顯示論文總數統計

## 輸出格式

終端輸出：表格形式顯示論文列表
- 不寫入 Obsidian
- 不進行 AI 分析
