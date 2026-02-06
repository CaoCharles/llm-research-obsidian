# AI 聊天機器人後端服務

本目錄包含 **LLM 評測知識庫** 的 AI 聊天機器人後端服務，使用 FastAPI 建置並整合 Google Gemini API。

---

## 📌 為什麼需要後端服務？

直接在前端呼叫 Gemini API 會導致 **API Key 外洩**，因為：

1. JavaScript 程式碼可在瀏覽器開發者工具中被檢視
2. API Key 一旦外洩，可能被濫用產生高額費用
3. 無法控制誰可以使用你的 API 配額

**解決方案**：建立後端 Proxy 服務，將 API Key 安全地存放在伺服器端。

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            使用者瀏覽器                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1. 訪問 GitHub Pages
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   GitHub Pages (前端靜態網站)                            │
│  caocharles.github.io/llm-research-obsidian                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 2. POST /api/chat
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Railway (後端 API 服務)                              │
│  FastAPI (chat_server.py) + GEMINI_API_KEY                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 3. 呼叫 Gemini API
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Google Cloud (Gemini 2.5 Flash)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 檔案結構

```
backend/
├── .python-version     # Python 版本 (3.12)
├── chat_server.py      # FastAPI 主程式
├── Dockerfile          # Docker 容器設定 (Python 3.12 + uv)
├── pyproject.toml      # Python 依賴套件
└── README.md           # 本文件
```

---

## 🔧 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 健康檢查，回傳 `{"status": "ok"}` |
| `/api/chat` | POST | 處理聊天請求 |

### 請求格式

```json
{
  "history": [
    {"role": "user", "parts": [{"text": "什麼是 LLM 評測？"}]},
    {"role": "model", "parts": [{"text": "LLM 評測是..."}]}
  ],
  "message": "如何設計評測指標？",
  "system_instruction": "你是 LLM 評測知識庫的助教..."
}
```

### 回應格式

```json
{
  "text": "設計評測指標時，需要考慮..."
}
```

---

## 🚀 本地開發

### 1. 設定環境變數

```bash
export GEMINI_API_KEY=your_api_key_here
```

> 📌 **取得 API Key**：前往 [Google AI Studio](https://aistudio.google.com/) 建立

### 2. 啟動後端服務

```bash
cd backend
uv sync
uv run uvicorn chat_server:app --reload --port 8001
```

### 3. 測試 API

```bash
curl http://localhost:8001/
```

---

## ☁️ 部署到 Railway

### Step 1：建立 Railway 專案

1. 前往 [Railway.app](https://railway.app/)
2. 點選 **New Project** → **Deploy from GitHub repo**
3. 選擇 `llm-research-obsidian` Repository

### Step 2：設定 Root Directory

1. 進入專案 **Settings**
2. 設定 **Root Directory**：`backend`

### Step 3：設定環境變數

在 **Variables** 標籤新增：

| Variable | Value |
|----------|-------|
| `GEMINI_API_KEY` | 你的 Gemini API Key |

### Step 4：取得公開網址

1. 進入 **Settings** → **Networking**
2. 點選 **Generate Domain**

---

## 🐛 疑難排解

| 問題 | 原因 | 解決 |
|------|------|------|
| Build Failed | 環境變數未設定 | 確認 `GEMINI_API_KEY` 已設定 |
| CORS Error | 前端網址未授權 | 修改 `allow_origins` 設定 |
| 回應很慢 | 免費方案服務睡眠 | 首次請求需喚醒，屬正常現象 |

---

## 📚 相關資源

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Railway 官方文件](https://docs.railway.app/)
- [Google Gemini API 文件](https://ai.google.dev/gemini-api/docs)
