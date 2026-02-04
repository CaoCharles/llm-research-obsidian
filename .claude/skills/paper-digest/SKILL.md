---
name: paper-digest
description: 執行完整的每日論文摘要流程
argument-hint: "[date] [top_n]"
---

# /paper-digest - 每日論文摘要

執行完整的每日論文摘要流程：抓取 → 篩選 → 分析 → 寫入 Obsidian。

## 參數

- `$ARGUMENTS[0]` - 日期（可選，預設今天，格式：YYYY-MM-DD 或 "today"）
- `$ARGUMENTS[1]` - Top N（可選，預設 5）

## 範例

```
/paper-digest              # 處理今天的論文，取 Top 5
/paper-digest 2025-02-03   # 處理指定日期
/paper-digest today 10     # 處理今天，取 Top 10
```

## 執行步驟

### Step 1: 抓取並篩選論文

執行 CLI 列出論文：

```bash
cd lpdd && uv run python cli.py list --top {top_n} [--date {date}]
```

顯示進度：「正在抓取 {date} 的論文...」

### Step 2: 逐篇分析論文

對於篩選出的每篇論文，進行深度分析。

對每篇論文生成以下結構化內容（使用繁體中文）：

```json
{
  "paper": {
    "arxiv_id": "論文 ID",
    "title": "論文標題",
    "abstract": "原文摘要",
    "authors": ["作者列表"],
    "categories": ["分類"],
    "published": "發布日期",
    "pdf_url": "PDF 連結"
  },
  "analysis": {
    "abstract_zh": "摘要的完整中文翻譯（保留技術術語英文，約200-300字）",
    "problem_statement": "論文解決什麼問題？現有方法有什麼不足？（100-150字）",
    "proposed_solution": "作者提出什麼解決方案或框架？核心創新點是什麼？（150-200字）",
    "core_contributions": ["核心貢獻1", "核心貢獻2", "核心貢獻3"],
    "methodology": "技術方法詳細說明（300-400字）",
    "key_results": "關鍵實驗結果，使用 Markdown 表格呈現",
    "insights": ["啟發1", "啟發2", "啟發3"],
    "limitations": "論文的限制（80-100字）",
    "tags": ["tag1", "tag2"],
    "relevance": 4,
    "related_topics": ["topic1", "topic2"],
    "category": "主分類"
  }
}
```

**可用的 tags**:
llm-as-judge, rag-evaluation, red-teaming, prompt-injection, faithfulness, hallucination, benchmark, safety, alignment, agent-evaluation

**relevance 評分（1-5）**:
- 5 = 突破性研究
- 4 = 有實用價值
- 3 = 可參考
- 2 = 間接相關
- 1 = 相關性低

顯示進度：「[{i}/{total}] 分析中: {title}...」

### Step 3: 寫入 Obsidian

將所有分析結果收集成 JSON 陣列，寫入暫存檔案。

對每篇論文執行寫入：

```bash
cd lpdd && uv run python cli.py write {paper_json_path}
```

### Step 4: 寫入每日摘要

將所有論文的分析結果寫入每日摘要：

```bash
cd lpdd && uv run python cli.py write-daily {all_papers_json_path} --date {date}
```

### Step 5: 回報結果

顯示總結：
- 處理日期
- 處理論文數量
- 各論文標題和相關度
- Obsidian 檔案路徑

## 輸出格式

終端輸出：顯示處理進度
Obsidian 寫入：
- Papers/{year}/{month}/[{arxiv_id}] {title}.md（每篇論文）
- Daily/{date}.md（每日摘要）
- 更新相關 Topics/ 頁面

## 注意事項

- 分析過程會消耗一些時間，請耐心等待
- 確保 OBSIDIAN_VAULT_PATH 環境變數已設定
- 論文 PDF 會自動下載到 PDFs/ 目錄
