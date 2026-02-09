# LLM 評測知識庫

> 系統化的 LLM 評測方法論、基準測試與安全評估學術指南

---

## 📑 LLM 評測與安全指南

網頁涵蓋企業級 LLM 品質驗證的完整框架，從評測指標定義到安全防禦策略：

[📥 下載完整評測與安全指南 (PDF)](PDFs/LLM_Evaluation_and_Safety_Guide.pdf)


![LLM Evaluation Guide](PDFs/LLM_Evaluation_and_Safety_Guide.pdf#navpanes=0&toolbar=0){ type=application/pdf style="min-height:60vh;width:100%" }

---

## 📘 Enterprise LLM Trust Blueprint

企業 LLM 信任治理藍圖文件：

[📥 下載 Enterprise LLM Trust Blueprint (PDF)](PDFs/Enterprise_LLM_Trust_Blueprint.pdf)

![Enterprise LLM Trust Blueprint](PDFs/Enterprise_LLM_Trust_Blueprint.pdf#navpanes=0&toolbar=0){ type=application/pdf style="min-height:60vh;width:100%" }

---

## 🎧 專題講解

<audio controls style="width:100%">
  <source src="assets/audio/專家如何幫_AI_模型打分數.m4a" type="audio/mp4">
</audio>

*專家如何幫 AI 模型打分數 — 深入解析評測方法論與業界實務*

---

## 📖 技術白皮書精華

!!! abstract "企業級 LLM 品質驗證體系"
    建立系統化評測體系是企業控管技術風險、優化運營成本與確保 ROI 的關鍵。相較於傳統軟體測試，LLM 驗證更像是一種統計推斷與語義審查的結合。

### 核心評測指標

| 指標 | 定義 | 驗證方法 |
|------|------|----------|
| **準確率** | 輸出與 Ground Truth 的精確匹配度 | Exact Match, ROUGE-L, LLM-as-Judge |
| **相關性** | 輸出對 Prompt 意圖的覆蓋程度 | RAGAS Context Relevance |
| **真實性** | 內容基於事實且無幻覺 | NLI, Self-CheckGPT |
| **一致性** | 相同輸入下的輸出穩定性 | Self-Consistency Check |
| **公平性** | 對不同群體的無偏見輸出 | 對抗性 Prompt 測試 |

### 四階段實施路徑

1. **架構定義期**：參考 HELM 框架，確立核心指標與權重
2. **數據建設期**：利用 CheckList 方法論建構黃金測試集
3. **工具自動化期**：導入 RAGAS 與 DeepEval 建立自動化評分
4. **安全加固期**：執行紅隊演練，部署 Llama Guard 等防護閘道

---

## 📚 知識庫內容

本知識庫整理 LLM 評測領域的學術研究與實務框架，涵蓋三大核心主題，協助 AI 架構師與開發團隊建立可靠的模型驗證流程。

---

### [評測策略與框架設計](Evaluation-Framework/index.md)

建立系統化評測方法論的理論基礎與實務指引：

- **評估指標體系**：準確率、相關性、真實性、一致性的學術定義與評估方法
- **Responsible AI 標準**：公平性、偏見檢測、可解釋性的研究進展與法規要求

核心研究：HELM (Liang et al., 2023)、LLM-as-Judge (Zheng et al., 2023)

---

### [基準測試與數據治理](Benchmark-Governance/index.md)

高品質評測資料集的設計原則與維護策略：

- **測試集設計**：黃金測試集、邊緣案例、對抗性樣本的方法論
- **評測工具**：RAGAS、DeepEval、Arize Phoenix 的理論基礎與應用指南

核心研究：CheckList (Ribeiro et al., 2020)、資料污染檢測 (Sainz et al., 2023)

---

### [安全性與紅隊演練](Security-RedTeam/index.md)

LLM 系統安全評估的學術框架與威脅防禦：

- **紅隊演練**：系統化安全測試的方法論與最佳實務
- **威脅防禦**：Prompt Injection、Jailbreaking、PII 洩露的研究與對策

核心研究：Red Teaming LLMs (Ganguli et al., 2022)、Jailbreak 機制 (Wei et al., 2023)

---

## 📄 論文庫

!!! success "收錄統計"
    目前已收錄並分析 **51 篇** LLM 相關論文

瀏覽收錄的 [LLM 相關論文](Papers/index.md)，包含深度分析與關鍵見解摘要。

---

## 📑 進階簡報：LLM 攻擊紅隊

探討 LLM 安全攻防的前沿技術與對抗策略：

[📥 下載LLM攻擊紅隊分析重點 (PDF)](PDFs/LLM攻擊紅隊前沿進階.pdf)



![LLM 攻擊紅隊](PDFs/LLM攻擊紅隊前沿進階.pdf#navpanes=0&toolbar=0){ type=application/pdf style="min-height:50vh;width:100%" }

---

## 學術資源

### 主要參考文獻

- Liang, P., et al. (2023). "Holistic Evaluation of Language Models (HELM)"
- Zheng, L., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
- Chang, Y., et al. (2024). "A Survey on Evaluation of Large Language Models"
- Ganguli, D., et al. (2022). "Red Teaming Language Models to Reduce Harms"
