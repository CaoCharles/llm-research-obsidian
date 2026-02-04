# LLM Paper Daily Digest - Claude Skills 使用指南

透過 Claude Code 的 Skills 功能，快速執行論文相關操作。

## 快速開始

### 1. 設定環境

```bash
# 設定 Obsidian Vault 路徑（預設使用專案根目錄）
# export OBSIDIAN_VAULT_PATH=/path/to/your/vault

# 進入專案目錄
cd llm-paper-obsidian/lpdd

# 安裝依賴
uv sync
```

### 2. 使用 Skills

在 Claude Code 中直接使用斜線命令：

```bash
/paper-list              # 列出今日論文
/paper-search "jailbreak"   # 搜尋論文
/paper-trending          # 查詢熱門論文
/paper-analyze 2502.00123   # 分析單篇
/paper-digest            # 每日摘要
```

---

## Skills 詳細說明

### `/paper-list` - 列出相關論文

列出當天相關度最高的論文（僅篩選，不進行 AI 分析）。

**參數：**
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `$0` | Top N 篇數 | 10 |
| `$1` | 日期 (YYYY-MM-DD) | 今天 |

**範例：**
```bash
/paper-list         # 列出今天 Top 10
/paper-list 20      # 列出今天 Top 20
/paper-list 10 2025-02-03  # 列出指定日期 Top 10
```

**輸出：**
- 終端表格顯示論文列表
- 不寫入 Obsidian

---

### `/paper-search` - 搜尋論文

用自訂關鍵字搜尋最近的論文。

**參數：**
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `$0` | 搜尋關鍵字（必填） | - |
| `$1` | 天數範圍 | 7 |

**範例：**
```bash
/paper-search "red team"      # 搜尋最近 7 天
/paper-search "jailbreak" 30  # 搜尋最近 30 天
/paper-search "prompt injection" 14
```

**輸出：**
- 終端表格顯示搜尋結果
- 按匹配次數排序
- 不寫入 Obsidian

---

### `/paper-trending` - 查詢熱門/經典論文

查詢 LLM 領域最近熱門或經典的論文。

**參數：**
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `$0` | 搜尋主題 | LLM evaluation |
| `--classic` | 搜尋經典論文 | 否（搜尋熱門） |

**範例：**
```bash
/paper-trending                    # 最近熱門的 LLM 論文
/paper-trending "red teaming"      # 紅隊測試熱門論文
/paper-trending "jailbreak" --classic  # jailbreak 經典論文
```

**輸出：**
- 終端表格顯示論文列表（含引用數）
- 可選擇下載並分析特定論文
- 資料來源：Semantic Scholar API

---

### `/paper-analyze` - 分析單篇論文

給定 arXiv ID，Claude 進行深度分析並寫入 Obsidian。

**參數：**
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `$0` | arXiv ID（必填） | - |

**範例：**
```bash
/paper-analyze 2502.00123
/paper-analyze 2501.12345
```

**輸出：**
- 終端顯示分析進度
- 寫入 `Papers/{year}/{month}/[{arxiv_id}] {title}.md`
- 更新相關 `Topics/` 頁面

**分析內容：**
- 摘要中文翻譯（200-300 字）
- 問題背景與現有方法不足
- 解決方案與核心創新點
- 技術方法詳述（300-400 字）
- 關鍵結果（Markdown 表格）
- 核心貢獻（3 點）
- 啟發與可應用見解
- 限制與未來工作

---

### `/paper-digest` - 每日論文摘要

執行完整的每日論文摘要流程。

**參數：**
| 參數 | 說明 | 預設值 |
|------|------|--------|
| `$0` | 日期 (YYYY-MM-DD 或 "today") | 今天 |
| `$1` | Top N 篇數 | 5 |

**範例：**
```bash
/paper-digest              # 處理今天的論文，取 Top 5
/paper-digest 2025-02-03   # 處理指定日期
/paper-digest today 10     # 處理今天，取 Top 10
```

**執行流程：**
1. 抓取指定日期的論文
2. 關鍵字權重篩選 Top N
3. Claude 逐篇深度分析
4. 寫入 Obsidian 論文筆記
5. 更新主題頁面
6. 生成每日摘要

**輸出：**
- 終端顯示處理進度
- 寫入 `Papers/{year}/{month}/` 論文筆記
- 寫入 `Daily/{date}.md` 每日摘要
- 更新 `Topics/` 主題頁面

---

## 環境變數

| 變數 | 說明 | 範例 |
|------|------|------|
| `OBSIDIAN_VAULT_PATH` | Obsidian Vault 路徑 | 專案根目錄 |

---

## 關鍵字權重

論文篩選使用 `keywords.yaml` 中定義的關鍵字權重：

| 類別 | 權重 | 範例關鍵字 |
|------|------|-----------|
| 核心 | 5 | llm-as-judge, jailbreak, prompt injection, red team |
| 評測 | 4 | hallucination, benchmark, faithfulness, evaluation |
| RAG | 4 | rag, retrieval-augmented, graphrag |
| 代理 | 4 | agentic, multi-agent, tool-use |
| 安全 | 3 | safety, alignment, toxicity |
| 其他 | 2-3 | reasoning, memory, synthetic data |

可在 `lpdd/keywords.yaml` 中自訂關鍵字和權重。

---

## 可用主題標籤

分析時使用的標籤：

- `llm-as-judge` - LLM 作為評審
- `rag-evaluation` - RAG 評測
- `red-teaming` - 紅隊測試
- `prompt-injection` - Prompt 注入
- `faithfulness` - 忠實度
- `hallucination` - 幻覺檢測
- `benchmark` - 基準測試
- `safety` - 安全性
- `alignment` - 對齊
- `agent-evaluation` - 代理評測

---

## Obsidian Vault 結構

```
llm-paper-obsidian/
├── Papers/
│   └── 2025/
│       └── 02/
│           ├── [2502.00123] Paper Title.md
│           └── ...
├── PDFs/
│   └── 2025/
│       └── 02/
│           ├── 2502.00123.pdf
│           └── ...
├── Topics/
│   ├── llm-as-judge.md
│   ├── benchmark.md
│   └── ...
└── Daily/
    └── 2025-02-04.md
```

---

## 常見問題

### Q: 如何更改篩選的最低分數？

修改 `lpdd/config.yaml`：

```yaml
filter:
  min_score: 5  # 調整此值
  top_n: 5
```

### Q: 如何新增關鍵字？

編輯 `lpdd/keywords.yaml`，在適當類別下新增：

```yaml
core:
  my-new-keyword: 5  # 關鍵字: 權重
```

### Q: 論文 PDF 在哪裡？

PDF 自動下載到 `{vault}/PDFs/{year}/{month}/` 目錄。

### Q: 如何只測試不寫入？

目前 Skills 會直接寫入 Obsidian。若要測試，建議先設定一個測試用的 Vault 路徑：

```bash
export OBSIDIAN_VAULT_PATH=./test-vault
```

---

## CLI 命令參考

Skills 底層使用的 CLI 命令：

```bash
# 列出論文
uv run python cli.py list --top 10 [--date 2025-02-03]

# 搜尋論文
uv run python cli.py search "keyword" --days 7

# 查詢熱門論文
uv run python cli.py trending "red teaming" --limit 10

# 查詢經典論文
uv run python cli.py trending "jailbreak" --classic

# 取得單篇論文
uv run python cli.py get 2502.00123

# 寫入 Obsidian
uv run python cli.py write /path/to/analysis.json

# 寫入每日摘要
uv run python cli.py write-daily /path/to/papers.json --date 2025-02-04
```

---

## 故障排除

### 找不到論文

arXiv API 可能有延遲，新論文可能需要一些時間才會出現。嘗試：
- 增加回溯時間（使用前一天的日期）
- 確認 arXiv ID 格式正確

### 寫入失敗

確認：
- `OBSIDIAN_VAULT_PATH` 環境變數已設定
- 目標目錄有寫入權限
- 模板檔案存在於 `lpdd/templates/`

### 網路錯誤

arXiv API 有速率限制，若遇到錯誤請稍後重試。
