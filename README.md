# LLM Paper Daily Digest - Obsidian + MkDocs

每日自動抓取 arXiv LLM 相關論文，透過 Claude Code 生成結構化摘要，寫入 Obsidian，同步到 MkDocs 網站。

## 專案摘要

- **資料來源**：arXiv（cs.CL / cs.AI / cs.CR）
- **流程**：抓取 → 篩選 → Claude 分析 → 寫入 Obsidian → 同步 MkDocs
- **輸出**：
  - 論文筆記：`Papers/`
  - PDF：`PDFs/`
  - 主題頁：`Topics/`
  - 每日摘要：`Daily/`
- **Skills**：`.claude/skills/`（Claude Code 指令）+ `.agent/skills/`（MkDocs/Chatbot 模板）

## 核心流程圖

```mermaid
graph TD
  U[你輸入問題/指令] --> S{Claude Skills}

  S -->|/paper-list| L[抓取 + 篩選清單]
  S -->|/paper-search| Q[關鍵字搜尋]
  S -->|/paper-trending| T[熱門/經典查詢]
  S -->|/paper-analyze| A[單篇分析 JSON]
  S -->|/paper-digest| D[每日摘要 JSON]

  A --> J1[/tmp/paper_<id>.json]
  D --> J2[/tmp/paper_<id>.json (多篇)/]

  J1 --> I[scripts/ingest_claude_json.py]
  J2 --> I

  I --> O[寫入 Obsidian Vault]
  O -->|Papers/ Topics/ Daily/ PDFs| OB[Obsidian 可直接閱讀]

  O --> SYNC[scripts/sync_docs.py]
  SYNC --> MK[docs/ 生成]
  MK --> BUILD[mkdocs build]
  BUILD --> SITE[GitHub Pages / 本機預覽]
```

## Skills 執行與更新路徑

### 1) 你輸入指令
- Claude Code 指令：`/paper-list`, `/paper-digest`, `/paper-analyze`, `/paper-search`, `/paper-trending`

### 2) Claude 生成 JSON
- 結果會輸出到：`/tmp/paper_<arxiv_id>.json`

### 3) 寫入 Obsidian（自動）
- 使用 `scripts/ingest_claude_json.py` 讀取 JSON 寫入：
  - `Papers/`
  - `Topics/`
  - `Daily/`
  - `PDFs/`

### 4) 同步 MkDocs
- `scripts/sync_docs.py` 把 Obsidian 內容同步到 `docs/`
- `mkdocs build` 產生網站

## 常用指令

### Claude Code 生成後匯入
```bash
python3 scripts/ingest_claude_json.py --dir /tmp --date 2026-02-05
```

### 同步到 MkDocs
```bash
python3 scripts/sync_docs.py
```

### 本機預覽
```bash
uv sync --project .agent/skills/mkdocs-setup/assets --no-install-project
uv run --project .agent/skills/mkdocs-setup/assets mkdocs serve
```

## 檔案結構

```
llm-paper-obsidian/
├── Daily/
├── PDFs/
├── Papers/
├── Topics/
├── docs/              # 由 sync_docs.py 生成
├── lpdd/              # 抓取/篩選/寫入程式
├── scripts/           # sync_docs / ingest_json
├── .claude/skills/    # Claude Code 指令 skills
└── .agent/skills/     # MkDocs/Chatbot skills 模板
```

## 技能整合

`.agent/skills` 與 `.claude/skills` 可雙向同步：

```bash
python3 scripts/sync_skills.py --prefer agent
```

## 相關文件

- 系統設計：`SDD.md`
- Skills 指南：`SKILLS_GUIDE.md`
