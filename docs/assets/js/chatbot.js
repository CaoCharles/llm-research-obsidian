// ====== AI 聊天機器人 ======
// LLM 評測知識庫

// ====== 全域狀態 ======
let chatContainer, chatMessages, chatInput, sendChatBtn;
let openChatBtn, closeChatBtn, toggleFullscreenBtn, clearHistoryBtn;

let allDocsContent = null;
let isContentLoading = false;
let chatHistory = [];

// ====== 設定 ======
// 部署後由 Cloud Run URL 取代此值。
window.BACKEND_API_URL = window.BACKEND_API_URL || "https://llm-research-chatbot-359359105644.asia-east1.run.app";

const isGitHubPages = window.location.hostname.includes('github.io');
const repoName = '/llm-research-obsidian';
const basePath = isGitHubPages ? repoName : '';
window.ALL_CONTENT_URL = window.ALL_CONTENT_URL || `${basePath}/content.json`;

window.INITIAL_PROMPT = "👋 嗨！我是 LLM 評測助教\n\n可以問我關於：\n📊 評測指標與框架\n🔬 RAGAS、DeepEval 工具\n🛡️ 紅隊演練與安全測試\n📄 論文摘要與見解";

// ====== 連結修正 ======
const BASE_URL = "https://CaoCharles.github.io/llm-research-obsidian";

function fixBrokenLinks(text) {
    return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return match;
        }
        if (url.startsWith('/')) {
            return `[${linkText}](${BASE_URL}${url})`;
        }
        if (!url.startsWith('#')) {
            return `[${linkText}](${BASE_URL}/${url})`;
        }
        return match;
    });
}

// ====== 小工具 ======
function rebuildChatFromHistory() {
    if (!chatMessages) return;
    chatMessages.innerHTML = "";
    chatHistory.forEach((turn) => {
        const sender = turn.role === "user" ? "user" : "bot";
        addMessage(sender, turn.parts[0].text, false);
    });
}

function saveHistory() {
    sessionStorage.setItem("geminiChatHistory", JSON.stringify(chatHistory));
}

function clearHistory() {
    chatHistory = [];
    sessionStorage.removeItem("geminiChatHistory");
    if (chatMessages) chatMessages.innerHTML = "";
    if (window.INITIAL_PROMPT) addMessage("bot", window.INITIAL_PROMPT);
}

function addCopyButtons(parentElement) {
    const codeBlocks = parentElement.querySelectorAll("pre");
    codeBlocks.forEach((block) => {
        const button = document.createElement("button");
        button.className = "copy-code-btn";
        button.textContent = "Copy";
        button.addEventListener("click", () => {
            const code = block.querySelector("code");
            if (navigator.clipboard && code) {
                navigator.clipboard.writeText(code.innerText).then(() => {
                    button.textContent = "Copied!";
                    setTimeout(() => { button.textContent = "Copy"; }, 2000);
                });
            }
        });
        block.appendChild(button);
    });
}

// ====== 訊息處理 ======
function addMessage(sender, text, addToHistory = true) {
    if (!chatMessages) return;

    const message = document.createElement("div");
    message.classList.add(sender === "user" ? "user-message" : "bot-message");

    if (sender === "bot" && typeof marked !== "undefined") {
        const fixedText = fixBrokenLinks(text);
        message.innerHTML = marked.parse(fixedText);
        addCopyButtons(message);
    } else {
        message.textContent = text;
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (addToHistory) {
        chatHistory.push({
            role: sender === "user" ? "user" : "model",
            parts: [{ text: text }],
        });
        saveHistory();
    }
}

function showTypingIndicator() {
    const indicator = document.createElement("div");
    indicator.classList.add("typing-indicator");
    indicator.id = "typing-indicator";
    indicator.innerHTML = "<span></span><span></span><span></span>";
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) indicator.remove();
}

// ====== 載入文件內容 ======
async function loadContent() {
    if (isContentLoading || allDocsContent) return;
    isContentLoading = true;

    try {
        const response = await fetch(window.ALL_CONTENT_URL);
        if (!response.ok) throw new Error("Failed to load content.json");

        const data = await response.json();
        allDocsContent = data.map((doc) =>
            `## ${doc.title}\nURL: ${doc.url}\n\n${doc.content}`
        ).join("\n\n---\n\n");

        if (window.INITIAL_PROMPT && chatHistory.length === 0) {
            addMessage("bot", window.INITIAL_PROMPT);
        }
    } catch (error) {
        console.error("Error loading content:", error);
        addMessage("bot", "⚠️ 無法載入文件內容，但仍可回答一般問題。");
    } finally {
        isContentLoading = false;
    }
}

// ====== 發送訊息 ======
async function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    addMessage("user", userMessage);
    chatInput.value = "";
    showTypingIndicator();

    const systemInstruction = `你是 LLM 評測知識庫的 AI 助教。

## 回答規則
1. 使用繁體中文回答
2. 使用文件中的完整 URL
3. 使用 Markdown 格式
4. 程式碼使用 \`\`\`bash 格式

## 課程文件
${allDocsContent || "文件載入中..."}`;

    try {
        const response = await fetch(`${window.BACKEND_API_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                history: chatHistory.slice(0, -1),
                message: userMessage,
                system_instruction: systemInstruction,
            }),
        });

        removeTypingIndicator();

        if (!response.ok) {
            let detail = `API 回應 ${response.status}`;
            try {
                const errorBody = await response.json();
                if (errorBody.detail) detail = errorBody.detail;
            } catch (_) {
                // Non-JSON errors keep the status-based message.
            }
            throw new Error(detail);
        }

        const data = await response.json();
        if (!data.text) throw new Error("API 未回傳文字內容");
        addMessage("bot", data.text);
    } catch (error) {
        removeTypingIndicator();
        addMessage("bot", `⚠️ 發生錯誤：${error.message}。請稍後再試。`);
        console.error("Chat error:", error);
    }
}

// ====== 注入 HTML ======
function injectChatbotHTML() {
    if (document.getElementById('gemini-chatbot')) return;

    const chatbotHTML = `
    <button id="open-chat">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30">
        <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
    </button>
    <div id="gemini-chatbot">
      <div id="chat-header">
        <span>AI Assistant</span>
        <div class="header-buttons">
          <button id="clear-history-btn" title="清除歷史">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
          <button id="toggle-fullscreen-btn" title="全螢幕">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
            </svg>
          </button>
          <button id="close-chat" title="關閉">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>
      <div id="chat-messages"></div>
      <div id="chat-input-container">
        <input type="text" id="chat-input" placeholder="輸入問題..." autocomplete="off">
        <button id="send-chat">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  `;
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);
}

// ====== 初始化 ======
function initChatbot() {
    injectChatbotHTML();

    chatContainer = document.getElementById("gemini-chatbot");
    chatMessages = document.getElementById("chat-messages");
    chatInput = document.getElementById("chat-input");
    sendChatBtn = document.getElementById("send-chat");
    openChatBtn = document.getElementById("open-chat");
    closeChatBtn = document.getElementById("close-chat");
    toggleFullscreenBtn = document.getElementById("toggle-fullscreen-btn");
    clearHistoryBtn = document.getElementById("clear-history-btn");

    if (!chatContainer || !openChatBtn) return;

    openChatBtn.addEventListener("click", () => {
        chatContainer.style.display = "flex";
        openChatBtn.style.display = "none";

        const savedHistory = sessionStorage.getItem("geminiChatHistory");
        if (savedHistory) {
            chatHistory = JSON.parse(savedHistory);
            rebuildChatFromHistory();
        }

        if (!allDocsContent) {
            loadContent();
        } else if (!savedHistory && window.INITIAL_PROMPT) {
            addMessage("bot", window.INITIAL_PROMPT);
        }
    });

    if (closeChatBtn) {
        closeChatBtn.addEventListener("click", () => {
            chatContainer.style.display = "none";
            openChatBtn.style.display = "block";
        });
    }

    if (toggleFullscreenBtn) {
        toggleFullscreenBtn.addEventListener("click", () => {
            chatContainer.classList.toggle("fullscreen");
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener("click", clearHistory);
    }

    if (sendChatBtn) {
        sendChatBtn.addEventListener("click", sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (openChatBtn) openChatBtn.style.display = 'block';
}

// ====== 啟動 ======
if (window.document$) {
    document$.subscribe(initChatbot);
} else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
} else {
    initChatbot();
}
