---
name: paper-analyze
description: 分析單篇 arXiv 論文並寫入 Obsidian
argument-hint: "<arxiv_id>"
---

# /paper-analyze - 分析單篇論文

給定 arXiv ID，進行深度分析並寫入 Obsidian。

## 參數

- `$ARGUMENTS[0]` - arXiv ID（必填，如 "2602.00123"）

## 範例

```
/paper-analyze 2602.00123
/paper-analyze 2602.04739
```

## 執行步驟

### Step 1: 抓取論文

執行 CLI 取得論文資料：

```bash
cd lpdd && uv run python cli.py get {arxiv_id}
```

### Step 2: 分析論文

讀取 CLI 輸出的 JSON，**深度閱讀並理解論文的完整內容**（包含方法細節、實驗設計、結果分析），然後生成以下結構化內容（使用繁體中文）：

**分析要求**:
1. **深度理解**: 不要只看摘要，要理解論文的核心創新、技術細節和實驗證據
2. **技術準確**: 保留關鍵技術術語的英文，確保翻譯準確不失真
3. **批判思考**: 分析論文的優勢、限制和潛在影響，提供有價值的見解
4. **實用導向**: 在「對我們的啟發」中提供可操作的洞察，而非空泛評論

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
    "abstract_zh": "摘要的完整中文翻譯（保留技術術語英文，約200-300字）\n準確傳達研究目標、方法和主要發現",

    "problem_statement": "論文解決什麼問題？現有方法有什麼不足？（100-150字）\n要點：明確指出研究動機、現有方法的局限性、為何這個問題重要",

    "proposed_solution": "作者提出什麼解決方案或框架？核心創新點是什麼？（150-200字）\n要點：說明方法的核心思想、創新之處、與現有方法的本質區別",

    "core_contributions": [
      "核心貢獻1（具體且可量化，說明技術創新或理論突破）",
      "核心貢獻2（強調實驗驗證或實用價值）",
      "核心貢獻3（如有第三個重要貢獻）"
    ],

    "methodology": "技術方法詳細說明（300-400字）\n必須包含：\n1. 模型架構或演算法流程\n2. 訓練/推理過程的關鍵步驟\n3. 資料集和預處理方式\n4. 評估指標和實驗設置\n5. 與 baseline 的對比方法",

    "key_results": "關鍵實驗結果（必須使用 Markdown 表格）\n要求：\n- 包含主要性能指標的數值對比\n- 展示本文方法相對於 baseline 的提升\n- 如有消融實驗，也應呈現關鍵結果\n- 表格要清晰、易讀、有對比性",

    "insights": [
      "洞察1（技術啟發：方法可以如何應用或改進）",
      "洞察2（理論啟發：揭示了什麼規律或原理）",
      "洞察3（實踐啟發：對實際部署或研究方向的建議）"
    ],

    "limitations": "論文的限制、不足或未來工作方向（80-100字）\n要點：客觀指出方法的適用範圍、實驗的局限、未解決的問題",

    "tags": ["標籤1", "標籤2", "標籤3（從下方分類中選擇2-4個最相關的）"],
    "relevance": 4,
    "related_topics": ["AI-Agent", "Safety-Alignment"（從6個主題資料夾中選擇）],
    "category": "最主要的分類（AI-Agent/Safety-Alignment/Hallucination/RAG/Benchmark/Multimodal）"
  }
}
```

**可用的 tags**（按主題資料夾分類）:

**AI-Agent**: agent, agent-evaluation, agent-benchmark, agentic-rag, embodied-ai, interactive-ai, tool-use, multi-agent
**Safety-Alignment**: safety, alignment, rlhf, red-teaming, jailbreak, prompt-injection, adversarial-robustness, certified-defense
**Hallucination**: hallucination, factuality, faithfulness, faithful-reasoning
**RAG**: rag, rag-evaluation, retrieval
**Benchmark**: benchmark, llm-as-judge, evaluation
**Multimodal**: multimodal, vlm, vision-language, multimodal-safety, omni-models, multimodal-reasoning

**related_topics 可用值**:
- AI-Agent, Safety-Alignment, Hallucination, RAG, Benchmark, Multimodal

**relevance 評分（1-5）**:
- 5 = 突破性研究（重大創新、開創性方法、顯著超越現有技術）
- 4 = 有實用價值（實用技術、可複現方法、明確應用場景）
- 3 = 可參考（有趣想法、部分創新、值得關注）
- 2 = 間接相關（邊緣議題、有限貢獻、參考價值低）
- 1 = 相關性低（主題不符、缺乏新意、價值有限）

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
- Papers/[{arxiv_id}] {title}.md
- 更新相關主題頁面（AI-Agent/, Safety-Alignment/, Hallucination/, RAG/, Benchmark/, Multimodal/）
