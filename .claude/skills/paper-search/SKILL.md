---
name: paper-search
description: 用自訂關鍵字搜尋最近的 arXiv 論文
argument-hint: "<keyword> [days]"
---

# /paper-search - 搜尋論文

用自訂關鍵字搜尋最近的 arXiv 論文。

## 參數

- `$ARGUMENTS[0]` - 搜尋關鍵字（必填）
- `$ARGUMENTS[1]` - 天數範圍（可選，預設 7）

## 範例

```
/paper-search "red team"      # 搜尋最近 7 天
/paper-search "jailbreak" 30  # 搜尋最近 30 天
/paper-search "prompt injection" 14
```

## 執行步驟

1. 解析參數：
   - 關鍵字: `$ARGUMENTS[0]`（必填，若未提供則提示使用者）
   - 天數: `$ARGUMENTS[1]` 或預設 7

2. 執行 CLI 搜尋論文：

```bash
cd lpdd && uv run python cli.py search "{keyword}" --days {days}
```

3. 將結果以表格形式顯示給使用者：

| 匹配數 | arXiv ID | 標題 | 發布日期 |
|--------|----------|------|----------|
| {score} | {arxiv_id} | {title} | {published} |

4. 顯示搜尋統計：
   - 關鍵字
   - 搜尋範圍（天數）
   - 找到的論文數量

## 輸出格式

終端輸出：表格形式顯示搜尋結果
- 不寫入 Obsidian
- 不進行 AI 分析

## 注意事項

- 關鍵字搜尋會在論文標題和摘要中進行全字匹配
- 結果按匹配次數排序
