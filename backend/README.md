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
│                   Google Cloud Run (後端 API 服務)                     │
│  FastAPI + 文件檢索快取 + Cloud Run service identity                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            content.json ──────────┘ 3. 擷取並檢索相關段落
                                    │ 4. 僅將最相關段落送給 Gemini
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Vertex AI (Gemini 3.5 Flash)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 檔案結構

```
backend/
├── .python-version     # Python 版本 (3.12)
├── chat_server.py      # FastAPI 主程式
├── retrieval.py        # 知識庫分段、檢索與快取
├── Dockerfile          # Docker 容器設定 (Python 3.12 + uv)
├── pyproject.toml      # Python 依賴套件
└── README.md           # 本文件
```

---

## 🔧 API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` 、`/api/health` | GET | 健康檢查，回傳後端與模型狀態 |
| `/api/chat` | POST | 處理聊天請求 |

### 請求格式

```json
{
  "history": [
    {"role": "user", "parts": [{"text": "什麼是 LLM 評測？"}]},
    {"role": "model", "parts": [{"text": "LLM 評測是..."}]}
  ],
  "message": "如何設計評測指標？"
}
```

### 回應格式

```json
{
  "text": "設計評測指標時，需要考慮...",
  "sources": [
    {"title": "評估指標", "url": "https://.../metrics/"}
  ]
}
```

前端不再下載整份 `content.json` 或傳送可修改的 system prompt。後端每 15 分鐘更新公開知識庫快取，依查詢只擷取最相關的頁面段落，並回傳可驗證的來源連結。

---

## 🚀 本地開發

### 1. 設定環境變數

```bash
export GEMINI_API_KEY=your_api_key_here
export GEMINI_MODEL=gemini-3.5-flash
export KNOWLEDGE_BASE_URL=https://caocharles.github.io/llm-research-obsidian/content.json
```

> 📌 **取得 API Key**：前往 [Google AI Studio](https://aistudio.google.com/) 建立。在 Cloud Run 生產環境建議改用 `GOOGLE_CLOUD_PROJECT` 與 Vertex AI IAM。

### 2. 啟動後端服務

```bash
cd backend
uv sync
uv run uvicorn chat_server:app --reload --port 8001
```

### 3. 測試 API

```bash
curl http://localhost:8001/api/health
```

---

## ☁️ 部署到 Google Cloud Run

```bash
gcloud services enable aiplatform.googleapis.com
gcloud run deploy llm-research-chatbot \
  --source=. \
  --region=asia-east1 \
  --allow-unauthenticated \
  --set-env-vars=GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=global,GEMINI_MODEL=gemini-3.5-flash,KNOWLEDGE_BASE_URL=https://caocharles.github.io/llm-research-obsidian/content.json
```

Cloud Run 執行帳號需要 `roles/aiplatform.user`。前端的 `BACKEND_API_URL` 必須指向部署完成後的 Cloud Run URL。

---

## 🐛 疑難排解

| 問題 | 原因 | 解決 |
|------|------|------|
| Build Failed | 環境變數未設定 | 確認 `GEMINI_API_KEY` 或 `GOOGLE_CLOUD_PROJECT` 已設定 |
| CORS Error | 前端網址未授權 | 修改 `allow_origins` 設定 |
| 回應很慢 | Cloud Run 冷啟動 | 首次請求可能需要數秒 |

---

## 📚 相關資源

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Railway 官方文件](https://docs.railway.app/)
- [Google Gemini API 文件](https://ai.google.dev/gemini-api/docs)
