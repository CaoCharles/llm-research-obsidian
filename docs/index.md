# LLM 評測知識庫

> 系統化的 LLM 評測方法論、基準測試與安全評估學術指南

## 📚 知識庫內容

本知識庫整理 LLM 評測領域的學術研究與實務框架，涵蓋評測指標、基準測試設計、安全評估三大核心主題。

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
    目前已收錄並分析 **35 篇** LLM 相關論文

瀏覽收錄的 [LLM 相關論文](Papers/index.md)，包含深度分析與關鍵見解摘要。

---

## 學術資源

### 主要參考文獻

- Liang, P., et al. (2023). "Holistic Evaluation of Language Models (HELM)"
- Zheng, L., et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
- Chang, Y., et al. (2024). "A Survey on Evaluation of Large Language Models"
- Ganguli, D., et al. (2022). "Red Teaming Language Models to Reduce Harms"
