# 可解釋性要求

> 確保 AI 決策過程透明、可理解、可追蹤

## 定義

**可解釋性**（Explainability）指能夠理解和解釋 AI 系統為何產生特定輸出的能力。對於高風險應用，可解釋性是法規和倫理的必要要求。

---

## 理論框架

### 可解釋性的層次

Lipton (2018) 區分了兩種可解釋性：

| 類型 | 定義 | 特點 |
|------|------|------|
| **透明性** | 模型內部機制可理解 | 線性模型、決策樹 |
| **事後解釋** | 為黑盒模型提供解釋 | LIME、SHAP、Attention |

### 解釋的受眾

Liao et al. (2020) 指出，不同受眾需要不同類型的解釋：

| 受眾 | 需求 |
|------|------|
| **最終使用者** | 為何得到這個結果？ |
| **領域專家** | 模型的推理是否合理？ |
| **開發者** | 模型如何做出決策？ |
| **監管者** | 決策過程是否合規？ |

---

## LLM 可解釋性研究

### 注意力機制分析

Attention 權重曾被視為解釋工具，但 Jain & Wallace (2019) 的研究質疑其有效性：

- Attention 權重與特徵重要性不一致
- 不同的 attention 分佈可能產生相同輸出

Wiegreffe & Pinter (2019) 則認為在特定條件下，attention 仍可提供有意義的解釋。

### Chain-of-Thought

Wei et al. (2022) 的 Chain-of-Thought（CoT）方法要求模型展示推理過程：

> 「讓我們一步步思考...」

CoT 的可解釋性價值：
- 使推理過程可視化
- 便於識別錯誤步驟
- 提升使用者信任

但 Turpin et al. (2023) 指出，CoT 解釋可能「事後合理化」而非反映真實推理過程。

### 自我解釋

Kadavath et al. (2022) 研究 LLM 的自我解釋能力：

- 模型可以為自己的輸出提供解釋
- 解釋的品質與模型規模正相關
- 但自我解釋可能仍是「編造」而非真實反映

---

## 解釋品質評估

### 評估維度

Jacovi & Goldberg (2020) 提出忠實性（faithfulness）與合理性（plausibility）的區分：

| 維度 | 定義 | 評估重點 |
|------|------|----------|
| **忠實性** | 解釋是否反映模型真實決策過程 | 操控解釋輸入後預測是否改變 |
| **合理性** | 解釋是否讓人類信服 | 人類評估者的接受度 |

### 評估方法

| 方法 | 測試目標 |
|------|----------|
| **刪除測試** | 移除解釋中重要部分，預測應改變 |
| **添加測試** | 只保留重要部分，預測應維持 |
| **人類評估** | 專家評估解釋的合理性 |
| **模擬測試** | 人類能否根據解釋預測模型行為 |

---

## 法規要求

### GDPR 第22條

「資料主體有權不受僅基於自動化處理的決定的約束...」

實務解讀：
- 使用者有權獲得有意義的解釋
- 需說明自動決策的邏輯
- 需說明預期後果

### EU AI Act

高風險 AI 系統需滿足透明性要求：
- 提供清晰的使用說明
- 解釋輸出的來源和邏輯
- 通知使用者正在與 AI 互動

---

## 相關主題

- [Responsible AI 標準](responsible-ai.md)
- [偏見檢測與緩解](bias-detection.md)

---

## 參考文獻

- Lipton, Z. C. (2018). "The Mythos of Model Interpretability"
- Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"
- Jacovi, A., & Goldberg, Y. (2020). "Towards Faithfully Interpretable NLP Systems: How Should We Define and Evaluate Faithfulness?"
- Turpin, M., et al. (2023). "Language Models Don't Always Say What They Think"
