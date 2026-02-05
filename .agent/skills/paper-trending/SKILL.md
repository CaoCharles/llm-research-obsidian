---
name: paper-trending
description: 查詢 LLM 領域熱門或經典論文
argument-hint: "[topic] [--classic]"
---

# /paper-trending - 查詢熱門/經典論文

查詢 LLM 領域最近熱門或經典的論文，可選擇下載並分析。

## 參數

- `$ARGUMENTS[0]` - 主題關鍵字（可選，預設搜尋 LLM 評測相關）
- `--classic` - 搜尋經典論文而非最近熱門（可選）

## 範例

```
/paper-trending                    # 最近熱門的 LLM 論文
/paper-trending "red teaming"      # 紅隊測試熱門論文
/paper-trending "jailbreak" --classic  # jailbreak 經典論文
/paper-trending --classic          # LLM 評測經典論文
```

## 執行步驟

### Step 1: 搜尋熱門論文

使用 Semantic Scholar API 或 Papers With Code 搜尋論文。

**搜尋條件：**
- 主題：使用者提供的關鍵字，或預設 "large language model evaluation"
- 熱門論文：按引用數 + 最近關注度排序
- 經典論文：按總引用數排序，發表時間較早

執行搜尋：

```bash
cd lpdd && uv run python cli.py trending "{topic}" [--classic]
```

若 CLI 尚未支援，則使用 WebSearch 搜尋：
- 搜尋 "most cited LLM {topic} papers 2024 2025"
- 或 "influential {topic} papers arxiv"

### Step 2: 整理並顯示結果

以表格形式顯示找到的論文：

| 排名 | 論文標題 | 作者 | 年份 | 引用數 | arXiv ID |
|------|----------|------|------|--------|----------|
| 1 | {title} | {authors} | {year} | {citations} | {arxiv_id} |

顯示每篇論文的：
- 標題
- 主要作者
- 發表年份
- 引用數（如有）
- arXiv ID 或連結

### Step 3: 詢問使用者

詢問使用者是否要：
1. 下載並分析特定論文
2. 將特定論文加入 Obsidian
3. 只查看不下載

**提示訊息：**
```
找到 {n} 篇相關論文。

請選擇要執行的操作：
1. 輸入論文編號（如 "1" 或 "1,3,5"）下載並分析
2. 輸入 "all" 下載所有論文
3. 輸入 "none" 或按 Enter 結束
```

### Step 4: 執行使用者選擇

若使用者選擇下載：

對每篇選中的論文執行 `/paper-analyze {arxiv_id}`：

```bash
cd lpdd && uv run python cli.py get {arxiv_id}
# 然後進行分析和寫入
```

## 輸出格式

終端輸出：
- 表格顯示熱門論文列表
- 互動式選擇要下載的論文

Obsidian 寫入（若選擇下載）：
- Papers/{year}/{month}/[{arxiv_id}] {title}.md
- 更新相關 Topics/ 頁面

## 熱門主題建議

可搜尋的熱門主題：
- `llm-as-judge` - LLM 作為評審
- `red teaming` - 紅隊測試
- `jailbreak` - 越獄攻擊
- `prompt injection` - Prompt 注入
- `hallucination` - 幻覺檢測
- `rag evaluation` - RAG 評測
- `benchmark` - 基準測試
- `alignment` - 對齊研究
- `agent` - 代理系統

## 注意事項

- 引用數來源可能因 API 限制而有所不同
- 部分論文可能沒有 arXiv ID
- 若搜尋 API 不可用，將使用 Web 搜尋作為備援
