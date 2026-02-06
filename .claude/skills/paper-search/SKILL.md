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

### Step 1: 解析參數

- 關鍵字: `$ARGUMENTS[0]`（必填，若未提供則提示使用者輸入）
- 天數: `$ARGUMENTS[1]` 或預設 7 天

若缺少關鍵字，友善提示：
```
請提供搜尋關鍵字。範例：
- /paper-search "jailbreak"
- /paper-search "adversarial robustness" 30
```

### Step 2: 執行搜尋

**優先嘗試 CLI**：

```bash
cd lpdd && uv run python cli.py search "{keyword}" --days {days}
```

**若 CLI 因 proxy/網路問題失敗，改用 WebSearch 備援**：

使用 WebSearch 工具搜尋：
- 搜尋關鍵字：`arxiv "{keyword}" LLM {current_year} {current_month} site:arxiv.org`
- 可進行多次搜尋以擴大覆蓋範圍
- 使用 WebFetch 取得論文詳細資訊（若 arxiv.org 被封鎖，從搜尋結果摘要中提取）
- 根據關鍵字匹配度排序結果

### Step 3: 顯示搜尋結果

將結果以清晰的表格形式呈現：

| # | arXiv ID | 標題 | 發布日期 | 匹配度 |
|---|----------|------|----------|--------|
| 1 | {arxiv_id} | {title} | {published} | {score} |
| 2 | ... | ... | ... | ... |

### Step 4: 提供後續操作選項

顯示搜尋統計並詢問使用者：
```
🔍 搜尋結果
關鍵字：{keyword}
範圍：最近 {days} 天
找到：{count} 篇相關論文

想要進一步分析某篇論文嗎？
- 輸入論文編號（如 "1" 或 "1,3,5"）以執行詳細分析
- 輸入 "all" 分析所有論文
- 按 Enter 結束
```

### Step 5: 執行使用者選擇（若有）

若使用者選擇分析論文，對每篇論文執行：
```bash
/paper-analyze {arxiv_id}
```

## 輸出格式

終端輸出：表格形式顯示搜尋結果
- 不寫入 Obsidian
- 不進行 AI 分析

## 注意事項

- 關鍵字搜尋會在論文標題和摘要中進行全字匹配
- 結果按匹配次數排序
