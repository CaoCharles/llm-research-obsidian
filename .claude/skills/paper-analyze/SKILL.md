---
name: paper-analyze
description: 分析單篇 arXiv 論文並寫入 Obsidian
argument-hint: "<arxiv_id>"
---

# /paper-analyze - 分析單篇論文

給定 arXiv ID，進行深度分析並寫入 Obsidian。

## 參數

- `$ARGUMENTS[0]` - arXiv ID（必填，如 "2502.00123"）

## 範例

```
/paper-analyze 2502.00123
/paper-analyze 2501.12345
```

## 執行步驟

### Step 1: 抓取論文

執行 CLI 取得論文資料：

```bash
cd lpdd && uv run python cli.py get {arxiv_id}
```

### Step 2: 分析論文

讀取 CLI 輸出的 JSON，分析論文並生成以下結構化內容（使用繁體中文）：

```json
{
  "paper": {
    "arxiv_id": "從 CLI 結果取得",
    "title": "從 CLI 結果取得",
    "abstract": "從 CLI 結果取得",
    "authors": ["從 CLI 結果取得"],
    "categories": ["從 CLI 結果取得"],
    "published": "從 CLI 結果取得",
    "pdf_url": "從 CLI 結果取得"
  },
  "analysis": {
    "abstract_zh": "摘要的完整中文翻譯（保留技術術語英文，約200-300字）",
    "problem_statement": "論文解決什麼問題？現有方法有什麼不足？（100-150字）",
    "proposed_solution": "作者提出什麼解決方案或框架？核心創新點是什麼？（150-200字）",
    "core_contributions": ["核心貢獻1（具體描述）", "核心貢獻2", "核心貢獻3"],
    "methodology": "技術方法詳細說明：包含模型架構、演算法步驟、資料處理方式、評估指標等（300-400字）",
    "key_results": "關鍵實驗結果，使用 Markdown 表格呈現主要數據對比",
    "insights": ["對我們的啟發1（可實際應用的見解）", "啟發2", "啟發3"],
    "limitations": "論文的限制、不足或未來工作方向（80-100字）",
    "tags": ["選擇 2-3 個標籤"],
    "relevance": 4,
    "related_topics": ["相關主題1", "相關主題2"],
    "category": "最主要的分類標籤"
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

### Step 3: 寫入 Obsidian

將分析結果寫入暫存 JSON 檔案，然後執行 CLI 寫入 Obsidian：

```bash
cd lpdd && uv run python cli.py write {json_file_path}
```

### Step 4: 回報結果

顯示以下資訊：
- 論文標題
- arXiv 連結
- 寫入的 Obsidian 檔案路徑
- 相關主題標籤

## 輸出格式

終端輸出：顯示分析進度和結果摘要
Obsidian 寫入：
- Papers/{year}/{month}/[{arxiv_id}] {title}.md
- 更新相關 Topics/ 頁面
