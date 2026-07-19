---
name: MkDocs 部署流程
description: LLM 評測知識庫的本地預覽與 GitHub Pages 部署流程
---

# MkDocs 部署流程 Skill

## 概述

本 Skill 定義 LLM 評測知識庫的部署流程，包含本地預覽、GitHub 提交、和 GitHub Pages 部署。

## 觸發條件

當使用者提到以下關鍵字時啟用：
- 部署、deploy、發布
- 預覽、serve、本地測試
- 推送、push、上傳

---

## 快速命令

### 本地預覽
```bash
uv run mkdocs serve
```
瀏覽器開啟：http://127.0.0.1:8000/

### 提交並推送
```bash
git add .
git commit -m "更新說明"
git push
```

### 部署到 GitHub Pages
```bash
uv run mkdocs gh-deploy --force
```

---

## 完整部署流程

```mermaid
graph LR
    A[修改檔案] --> B[git add .]
    B --> C[git commit]
    C --> D[git push]
    D --> E[mkdocs gh-deploy]
    E --> F[GitHub Pages 更新]
```

### 步驟 1：本地預覽確認
```bash
uv run mkdocs serve
```
- 檢查頁面排版
- 確認 Mermaid 圖表正常
- 測試連結是否正確

### 步驟 2：提交變更
```bash
git add .
git commit -m "描述你的變更"
git push
```

### 步驟 3：部署到 GitHub Pages
```bash
uv run mkdocs gh-deploy --force
```

**預期輸出**：
```
INFO    -  Your documentation should shortly be available at: https://CaoCharles.github.io/llm-research-obsidian/
```

---

## 網站結構

### 目前主題

| 主題 | 頁面數 | 內容 |
|------|--------|------|
| **評測策略與框架** | 9 | 準確率、相關性、真實性、一致性、Responsible AI |
| **基準測試與數據治理** | 9 | 黃金測試集、評測工具（RAGAS、DeepEval、Arize）|
| **安全性與紅隊演練** | 8 | Jailbreaking、Prompt Injection、PII 防護 |
| **論文庫** | N | 收錄的 LLM 相關論文 |

### 專案特殊設定

**自動生成 content.json**：
- Hook 腳本：`.agent/skills/chatbot-setup/assets/generate_content.py`
- 在建置時自動生成供 AI Chatbot 使用

---

## 故障排除

### 問題：部署後頁面沒更新
**解決**：清除瀏覽器快取，或等待 1-2 分鐘

### 問題：Mermaid 圖表不顯示
**解決**：確認 `mkdocs.yml` 有正確設定 superfences

### 問題：content.json 沒有生成
**解決**：確認 hooks 設定正確

---

## 相關檔案

| 檔案 | 說明 |
|------|------|
| `mkdocs.yml` | MkDocs 主設定檔 |
| `docs/index.md` | 首頁 |
| `docs/Evaluation-Framework/` | 評測策略章節 |
| `docs/Benchmark-Governance/` | 基準測試章節 |
| `docs/Security-RedTeam/` | 安全性章節 |
