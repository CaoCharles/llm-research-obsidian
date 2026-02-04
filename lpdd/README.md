# LLM Paper Daily Digest - Obsidian 版

自動化論文摘要系統：每日從 arXiv 抓取 LLM 評測相關論文，使用 AI 分析，寫入 Obsidian Vault。

---

## Claude Skills 快速開始

透過 Claude Code 的 Skills 功能，直接使用斜線命令：

```bash
/paper-list              # 列出今日相關論文
/paper-search "jailbreak"  # 搜尋特定關鍵字
/paper-trending          # 查詢熱門/經典論文
/paper-analyze 2502.00123  # 分析單篇論文
/paper-digest            # 每日摘要（完整流程）
```

**設定環境變數：**

```bash
# 預設使用專案根目錄，可自訂
# export OBSIDIAN_VAULT_PATH=/path/to/your/vault
```

詳細說明請參考 [SKILLS_GUIDE.md](../SKILLS_GUIDE.md)。

---

## 功能特色

- 🔍 **arXiv 抓取**：自動抓取 cs.CL、cs.AI、cs.CR 分類的最新論文（每日約 200 篇）
- 🎯 **關鍵字篩選**：依權重篩選 Top 5 最相關論文
- 🤖 **AI 深度分析**：使用 Claude 生成詳細結構化摘要（透過 Claude Code Skills）
- 📄 **PDF 自動下載**：論文 PDF 自動下載並嵌入 Obsidian
- 📝 **Obsidian 寫入**：自動建立論文筆記、主題頁和每日摘要
- ⚡ **Claude Skills**：透過 `/slash-command` 快速執行論文操作

---

## 執行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Paper Daily Digest                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 抓取 arXiv 論文 (fetcher.py)                              │
│    • 查詢 cs.CL, cs.AI, cs.CR 分類                          │
│    • 抓取最近 24 小時的論文（約 200 篇）                      │
│    • 輸出: list[Paper]                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 關鍵字篩選 (filter.py)                                    │
│    • 載入 keywords.yaml 權重配置                             │
│    • 計算每篇論文的相關度分數                                 │
│    • 篩選 Top 5 最高分論文                                   │
│    • 輸出: list[Paper] (最多 5 篇)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GPT 深度分析 (analyzer.py)                                │
│    • 呼叫 OpenAI GPT-5-mini API                             │
│    • 生成結構化分析：                                        │
│      - 摘要中文翻譯（200-300 字）                            │
│      - 問題背景（100-150 字）                                │
│      - 解決方案（150-200 字）                                │
│      - 技術方法詳述（300-400 字）                            │
│      - 關鍵結果（Markdown 表格）                             │
│      - 核心貢獻、啟發、限制                                  │
│    • 含重試機制（失敗自動重試 2 次）                          │
│    • 輸出: list[(Paper, AnalysisResult)]                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 寫入 Obsidian (writer.py)                                 │
│    • 下載論文 PDF 到 PDFs/ 目錄                              │
│    • 生成論文筆記（含 PDF 嵌入預覽）                          │
│    • 更新主題彙整頁（雙向連結）                               │
│    • 生成每日摘要頁                                          │
│    • 輸出: Obsidian Vault 檔案                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 安裝

```bash
cd lpdd

# 使用 uv 安裝依賴
uv sync
```

## 設定

1. 設定 OpenAI API Key：

```bash
export OPENAI_API_KEY=your-api-key
# 或在 .env 檔案中設定
```

2. 修改 `config.yaml` 中的 Obsidian Vault 路徑：

```yaml
obsidian:
  vault_path: /Users/caocharles/Library/CloudStorage/OneDrive-個人/GitHub/claude_test/llm-paper-obsidian
```

## 使用方式

```bash
# 執行（抓取最近 24 小時論文）
uv run python main.py

# 指定日期補抓
uv run python main.py --date 2025-02-03

# 指定 Vault 路徑
uv run python main.py --vault ./my-vault

# 模擬執行（不呼叫 AI、不寫入檔案）
uv run python main.py --dry-run
```

---

## 輸出結構

```
llm-paper-obsidian/
├── Papers/
│   └── 2026/
│       └── 02/
│           ├── [2602.03652] RAGTurk - Best Practices for....md
│           └── ...
├── PDFs/
│   └── 2026/
│       └── 02/
│           ├── 2602.03652.pdf
│           └── ...
├── Topics/
│   ├── llm-as-judge.md              # 主題彙整頁
│   └── benchmark.md
└── Daily/
    └── 2026-02-04.md                # 每日摘要
```

---

## 論文筆記結構

每篇論文筆記包含：

| 區塊 | 說明 |
|------|------|
| 摘要（中文翻譯） | 200-300 字完整翻譯 |
| 問題背景 | 解決什麼問題、現有方法不足 |
| 解決方案 | 提出的框架/方法、核心創新點 |
| 技術方法 | 架構、演算法、資料集、評估指標 |
| 關鍵結果 | Markdown 表格呈現 |
| 核心貢獻 | 3 個主要貢獻點 |
| 啟發 | 可實際應用的見解（Checkbox） |
| 限制 | 不足與未來工作 |
| PDF 預覽 | 嵌入本地 PDF 第一頁 |

---

## 關鍵字權重

可在 `keywords.yaml` 中調整：

| 類別 | 權重 | 範例 |
|------|------|------|
| 核心 | 5 | llm-as-judge, jailbreak, prompt injection |
| 評測 | 4 | hallucination, benchmark, faithfulness |
| RAG | 3 | rag, retrieval-augmented |
| 其他 | 2 | accuracy, consistency |

---

## 專案結構

```
lpdd/
├── config.yaml      # 系統設定
├── keywords.yaml    # 關鍵字權重
├── main.py          # 主程式入口
├── fetcher.py       # arXiv API 抓取
├── filter.py        # 關鍵字權重篩選
├── analyzer.py      # GPT 分析（含重試）
├── writer.py        # Obsidian 寫入（含 PDF 下載）
├── models.py        # 資料模型定義
├── pyproject.toml   # uv 專案配置
└── templates/       # Jinja2 模板
    ├── paper.md     # 論文筆記模板
    ├── topic.md     # 主題頁模板
    └── daily.md     # 每日摘要模板
```

---

## 授權

MIT License
