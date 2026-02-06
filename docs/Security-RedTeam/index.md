# 安全性與紅隊演練

> LLM 系統安全評估的學術框架與實務方法

## 概述

隨著 LLM 在關鍵應用場景的普及，安全性評估成為學術研究和產業實務的核心議題。Ganguli et al. (2022) 指出：「安全對齊的模型仍可能被繞過，系統化的安全評估是必要的。」

本章節整理 LLM 安全評估的學術研究與實務框架。

---

## 研究背景

### LLM 安全的獨特挑戰

與傳統軟體安全相比，LLM 安全面臨獨特挑戰：

| 傳統安全 | LLM 安全 |
|----------|----------|
| 明確的輸入規格 | 開放式自然語言輸入 |
| 確定性行為 | 隨機性輸出 |
| 程式邏輯漏洞 | 對齊與意圖理解問題 |
| 可形式化驗證 | 難以完全形式化 |

### 安全研究的演進

| 階段 | 研究重點 | 代表工作 |
|------|----------|----------|
| **早期** | 偏見與有害內容 | Gehman et al. (2020) |
| **對齊時代** | RLHF 安全性 | Ganguli et al. (2022) |
| **現代** | 紅隊與對抗攻擊 | Perez et al. (2022) |

---

## 核心議題

### 安全防護機制

多層次的安全架構設計：

- [AI 安全防護](ai-security.md) - 輸入過濾、輸出檢查、系統設計

### 主動式安全評估

紅隊演練的方法論：

- [紅隊演練指南](red-teaming-guide.md) - 系統化的安全測試流程
- [攻擊向量清單](attack-vectors.md) - 已知威脅類型整理

### 特定威脅防禦

針對主要威脅類型的防禦策略：

- [Prompt Injection 防禦](defense-prompt-injection.md)
- [Jailbreaking 防禦](defense-jailbreaking.md)
- [PII 洩露防護](defense-pii.md)

### 系統可靠性

- [壓力測試標準](stress-testing.md) - 高負載下的安全性維持

---

## 學術分類框架

### 威脅模型

根據攻擊者能力分類：

| 威脅等級 | 攻擊者能力 | 範例 |
|----------|------------|------|
| **Level 0** | 普通使用者 | 簡單的繞過嘗試 |
| **Level 1** | 熟悉系統的使用者 | 了解常見 Jailbreak |
| **Level 2** | 技術專家 | 設計客製化攻擊 |
| **Level 3** | 研究者 | 發現新型攻擊向量 |

### 攻擊表面

Greshake et al. (2023) 將 LLM 攻擊表面分為：

| 攻擊向量 | 說明 |
|----------|------|
| **直接互動** | 使用者直接輸入惡意提示 |
| **間接注入** | 透過外部資料源植入 |
| **系統層** | 攻擊基礎設施 |
| **供應鏈** | 污染訓練資料或模型權重 |

---

## 評估標準

### 安全性評測指標

| 指標 | 定義 |
|------|------|
| **攻擊成功率 (ASR)** | 成功繞過安全機制的比例 |
| **誤拒率 (FRR)** | 誤擋正常請求的比例 |
| **漏報率 (FNR)** | 未識別有害請求的比例 |

### 安全基準

| 基準 | 內容 | 提出者 |
|------|------|--------|
| **AdvBench** | 對抗性 Jailbreak 測試 | Zou et al. (2023) |
| **TruthfulQA** | 錯誤資訊生成測試 | Lin et al. (2022) |
| **RealToxicityPrompts** | 有害內容生成測試 | Gehman et al. (2020) |

---

## 相關主題

- [評測策略與框架設計](../Evaluation-Framework/index.md)
- [基準測試與數據治理](../Benchmark-Governance/index.md)
- [對抗性樣本](../Benchmark-Governance/adversarial-samples.md)

---

## 參考文獻

- Ganguli, D., et al. (2022). "Red Teaming Language Models to Reduce Harms"
- Greshake, K., et al. (2023). "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"
- Perez, E., et al. (2022). "Red Teaming Language Models with Language Models"
