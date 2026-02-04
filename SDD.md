# Software Design Document (SDD)
# LLM Paper Daily Digest - Obsidian 版

**版本**: 1.0  
**日期**: 2025-02-04  
**範圍**: 每日抓取 arXiv 論文 → AI 分析 → 寫入 Obsidian（含雙向連結）

---

## 1. 專案目標

建立一個自動化系統：
1. 每日從 arXiv 抓取 LLM 評測相關論文
2. 使用 Claude 分析並生成結構化筆記
3. 寫入 Obsidian Vault，自動建立論文之間的雙向連結

---

## 2. 系統流程

```
每日執行 (08:00)
      │
      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   arXiv     │────▶│  關鍵字     │────▶│   Claude    │
│   抓取      │     │  篩選       │     │   分析      │
│  (~100篇)   │     │  (~15篇)    │     │  (Top 5篇)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │  Obsidian   │
                                        │  寫入       │
                                        └─────────────┘
```

---

## 3. Obsidian 結構

```
LLM-Research-Obsidian/
│
├── Papers/
│   └── 2025/
│       └── 02/
│           ├── 2502.00123.md      # 單篇論文筆記
│           ├── 2502.00456.md
│           └── ...
│
├── Topics/
│   ├── llm-as-judge.md            # 主題彙整頁
│   ├── rag-evaluation.md
│   ├── red-teaming.md
│   ├── hallucination.md
│   ├── benchmark.md
│   └── prompt-injection.md
│
├── Daily/
│   └── 2025-02-04.md              # 每日摘要
│
└── templates/
    ├── paper-template.md
    └── daily-template.md
```

---

## 4. 論文筆記格式

### 4.1 Frontmatter (YAML)

```yaml
---
arxiv_id: "2502.00123"
title: "論文標題"
date: 2025-02-04
authors:
  - Alice Chen
  - Bob Smith
institution: Google DeepMind
tags:
  - llm-as-judge
  - benchmark
  - faithfulness
relevance: 4
status: unread
---
```

### 4.2 完整筆記模板

```markdown
---
arxiv_id: "{{arxiv_id}}"
title: "{{title}}"
date: {{date}}
authors: {{authors}}
institution: "{{institution}}"
tags: {{tags}}
relevance: {{relevance}}
status: unread
---

# {{title}}

## 連結
- [arXiv](https://arxiv.org/abs/{{arxiv_id}})
- [PDF](https://arxiv.org/pdf/{{arxiv_id}})

## 三句話總結
> {{one_liner}}

## 核心貢獻
{{core_contributions}}

## 方法
{{methodology}}

## 關鍵結果
{{key_results}}

## 對我們的啟發
{{insights}}

## 相關論文
{{related_papers}}

## 筆記
（手動補充）
```

---

## 5. 雙向連結規則

### 5.1 論文之間的連結

AI 分析時，若發現與其他論文相關，自動產生連結：

```markdown
## 相關論文
- [[2502.00456]] - 類似的評測框架
- [[2501.12345]] - 本文引用的基礎方法
- [[Topics/llm-as-judge]] - 相關主題
```

### 5.2 主題頁自動更新

每篇新論文寫入後，更新對應的主題頁：

```markdown
# LLM-as-Judge

## 最新論文
- [[2502.00123]] - 提出小模型評審方案 (2025-02-04)
- [[2502.00456]] - 評審偏見分析 (2025-02-03)

## 所有相關論文
```dataview
LIST
FROM "Papers"
WHERE contains(tags, "llm-as-judge")
SORT date DESC
```
```

---

## 6. 功能規格

### F01: arXiv 抓取

```python
@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    authors: list[str]
    categories: list[str]
    published: datetime
    pdf_url: str

def fetch_papers(categories: list[str], hours: int = 24) -> list[Paper]:
    """
    從 arXiv 抓取論文
    
    Args:
        categories: ["cs.CL", "cs.AI", "cs.CR"]
        hours: 回溯時數，預設 24
    
    Returns:
        論文列表，預期 100-150 篇
    """
    pass
```

### F02: 關鍵字篩選

```python
KEYWORDS = {
    # 核心 (權重 5)
    "llm-as-judge": 5,
    "red team": 5,
    "jailbreak": 5,
    "prompt injection": 5,
    
    # 評測 (權重 4)
    "faithfulness": 4,
    "hallucination": 4,
    "benchmark": 4,
    
    # RAG (權重 3)
    "rag": 3,
    "evaluation": 3,
    "retrieval-augmented": 3,
    
    # 其他 (權重 2)
    "accuracy": 2,
    "consistency": 2,
}

def filter_papers(papers: list[Paper], min_score: int = 5) -> list[Paper]:
    """
    依關鍵字權重篩選
    
    Returns:
        篩選後論文，預期 10-20 篇
    """
    pass
```

### F03: AI 分析

```python
ANALYSIS_PROMPT = """
你是 LLM 評測專家。請分析這篇論文：

標題: {title}
摘要: {abstract}

請用繁體中文回答，輸出 JSON 格式：
{{
    "one_liner": "一句話總結（30字內）",
    "core_contributions": ["貢獻1", "貢獻2", "貢獻3"],
    "methodology": "方法簡述（50字內）",
    "key_results": "關鍵結果（可含表格）",
    "insights": ["啟發1", "啟發2"],
    "tags": ["tag1", "tag2"],
    "relevance": 4,
    "related_topics": ["llm-as-judge", "benchmark"]
}}

可用的 tags: llm-as-judge, rag-evaluation, red-teaming, 
prompt-injection, faithfulness, hallucination, benchmark, 
safety, alignment, agent-evaluation
"""

def analyze_paper(paper: Paper, claude_client) -> dict:
    """
    使用 Claude 分析論文
    
    Returns:
        分析結果 dict
    """
    pass
```

### F04: Obsidian 寫入

```python
def write_paper_note(paper: Paper, analysis: dict, vault_path: Path):
    """
    寫入論文筆記到 Obsidian
    
    路徑: {vault}/Papers/{year}/{month}/{arxiv_id}.md
    """
    pass

def update_topic_page(topic: str, paper: Paper, vault_path: Path):
    """
    更新主題頁面，加入新論文連結
    
    路徑: {vault}/Topics/{topic}.md
    """
    pass

def write_daily_summary(papers: list[Paper], date: str, vault_path: Path):
    """
    寫入每日摘要
    
    路徑: {vault}/Daily/{date}.md
    """
    pass
```

---

## 7. 設定檔

```yaml
# config.yaml

# arXiv 設定
arxiv:
  categories:
    - cs.CL
    - cs.AI
    - cs.CR
  hours_lookback: 24
  max_results: 200

# 篩選設定
filter:
  min_score: 5
  top_n: 5  # 送去 AI 分析的數量

# Claude 設定
claude:
  model: claude-sonnet-4-20250514
  max_tokens: 2000

# Obsidian 設定
obsidian:
  vault_path: ~/Obsidian/LLM-Research
  
# 可用主題標籤
topics:
  - llm-as-judge
  - rag-evaluation
  - red-teaming
  - prompt-injection
  - faithfulness
  - hallucination
  - benchmark
  - safety
  - alignment
  - agent-evaluation
```

---

## 8. 目錄結構

```
lpdd/
├── config.yaml           # 設定檔
├── keywords.yaml         # 關鍵字權重
├── main.py              # 主程式
├── fetcher.py           # arXiv 抓取
├── filter.py            # 關鍵字篩選
├── analyzer.py          # Claude 分析
├── writer.py            # Obsidian 寫入
├── models.py            # 資料模型
└── templates/
    ├── paper.md         # 論文模板
    ├── topic.md         # 主題頁模板
    └── daily.md         # 每日摘要模板
```

---

## 9. 執行方式

```bash
# 安裝依賴
pip install arxiv anthropic pyyaml jinja2

# 設定環境變數
export ANTHROPIC_API_KEY=your-key

# 執行
python main.py

# 或指定日期補抓
python main.py --date 2025-02-03
```

---

## 10. 主程式流程

```python
# main.py

def main():
    # 1. 載入設定
    config = load_config("config.yaml")
    
    # 2. 抓取論文
    papers = fetch_papers(
        categories=config["arxiv"]["categories"],
        hours=config["arxiv"]["hours_lookback"]
    )
    print(f"抓取到 {len(papers)} 篇論文")
    
    # 3. 關鍵字篩選
    filtered = filter_papers(papers, min_score=config["filter"]["min_score"])
    print(f"篩選後 {len(filtered)} 篇")
    
    # 4. 取 Top N 進行 AI 分析
    top_papers = filtered[:config["filter"]["top_n"]]
    
    # 5. AI 分析
    claude = ClaudeClient(model=config["claude"]["model"])
    results = []
    for paper in top_papers:
        analysis = analyze_paper(paper, claude)
        results.append((paper, analysis))
        print(f"已分析: {paper.title[:50]}...")
    
    # 6. 寫入 Obsidian
    vault_path = Path(config["obsidian"]["vault_path"]).expanduser()
    
    for paper, analysis in results:
        write_paper_note(paper, analysis, vault_path)
        for topic in analysis["related_topics"]:
            update_topic_page(topic, paper, vault_path)
    
    # 7. 寫入每日摘要
    today = datetime.now().strftime("%Y-%m-%d")
    write_daily_summary([p for p, _ in results], today, vault_path)
    
    print(f"完成！已寫入 {len(results)} 篇論文筆記")

if __name__ == "__main__":
    main()
```

---

## 11. 預期產出範例

### 論文筆記範例

**檔案**: `Papers/2025/02/2502.00123.md`

```markdown
---
arxiv_id: "2502.00123"
title: "Small Models as LLM Judges: A Cost-Effective Alternative"
date: 2025-02-04
authors:
  - Alice Chen
  - Bob Smith
institution: Google DeepMind
tags:
  - llm-as-judge
  - benchmark
relevance: 5
status: unread
---

# Small Models as LLM Judges: A Cost-Effective Alternative

## 連結
- [arXiv](https://arxiv.org/abs/2502.00123)
- [PDF](https://arxiv.org/pdf/2502.00123)

## 一句話總結
> 使用微調後的 7B 模型取代 GPT-4 作為評審，成本降低 90%。

## 核心貢獻
1. 證明小模型經微調可達 GPT-4 評審能力的 95%
2. 開源 10K 樣本的評審訓練數據集
3. 提出 calibration 方法解決評分偏差

## 方法
使用 GPT-4 生成評審數據，對 Llama-2-7B 進行 SFT，並透過溫度調整校準。

## 關鍵結果
| 模型 | 人類一致性 | 成本/1K | 延遲 |
|------|-----------|---------|------|
| GPT-4 | 85% | $100 | 2.1s |
| 7B (ours) | 82% | $10 | 0.3s |

## 對我們的啟發
- [ ] 評估導入小模型評審的可行性
- [ ] 用 Golden Dataset 微調專屬評審模型

## 相關論文
- [[Topics/llm-as-judge]]
- [[Topics/benchmark]]

## 筆記
（手動補充）
```

### 每日摘要範例

**檔案**: `Daily/2025-02-04.md`

```markdown
# 2025-02-04 論文摘要

今日分析 **5** 篇 LLM 評測相關論文。

## 今日論文

| 論文 | 主題 | 相關度 |
|------|------|--------|
| [[2502.00123]] | 小模型評審 | ⭐⭐⭐⭐⭐ |
| [[2502.00456]] | RAG 評測框架 | ⭐⭐⭐⭐ |
| [[2502.00789]] | Prompt Injection 防禦 | ⭐⭐⭐⭐ |
| [[2502.01012]] | 幻覺檢測 | ⭐⭐⭐⭐ |
| [[2502.01345]] | Agent 評測 | ⭐⭐⭐ |

## 重點發現
- 小模型評審成為趨勢，成本可降低 90%
- RAG 評測開始關注多跳推理場景
```

---

## 12. 開發優先順序

1. **Phase 1** (本次)
   - [x] 定義 Obsidian vault 結構
   - [ ] 實作 arXiv 抓取
   - [ ] 實作關鍵字篩選
   - [ ] 實作 Claude 分析
   - [ ] 實作 Obsidian 寫入（含雙向連結）

2. **Phase 2** (未來)
   - [ ] 週報自動生成
   - [ ] MkDocs 同步
   - [ ] 歷史論文回補

---

**文件結束**