# 相關性 (Relevance)

> 評估模型輸出是否切題、是否回答使用者真正的問題

## 定義

**相關性**（Relevance）衡量模型輸出與使用者查詢或意圖的語義匹配程度。在資訊檢索和問答系統中，相關性是核心評估維度。

---

## 理論基礎

### 相關性的多層次定義

Saracevic (2007) 提出相關性的多層次模型：

| 層次 | 定義 | 範例 |
|------|------|------|
| **主題相關** | 是否在正確的主題範圍內 | 問程式問題，答案涉及程式設計 |
| **認知相關** | 是否提供使用者所需的資訊 | 回答解決使用者的實際問題 |
| **情境相關** | 是否考慮對話上下文 | 多輪對話中的指代消解 |

### 相關性與正確性的區別

相關性與準確率是不同的維度：

- **相關但不正確**：回答切題但內容有誤
- **正確但不相關**：內容正確但未回答問題
- **理想狀態**：既相關又正確

---

## 評估方法

### 基於嵌入的語義相似度

透過預訓練語言模型計算語義相似度：

| 方法 | 特點 |
|------|------|
| **Sentence-BERT** | 專門訓練的句子嵌入模型 |
| **SimCSE** | 對比學習增強的句子表示 |
| **E5** | 大規模訓練的通用嵌入模型 |

Reimers & Gurevych (2019) 的 Sentence-BERT 研究顯示，語義相似度可以有效捕捉句子間的關聯性，是評估相關性的有效工具。

### LLM-as-Judge 評估

使用大型語言模型作為評審評估相關性。Es et al. (2024) 在 RAGAS 框架中定義 Answer Relevancy：

> 「評估生成的答案與給定問題的相關程度。理想的答案應該直接回應問題的核心需求。」

評估維度包括：
- 答案是否直接回應問題
- 是否包含不必要的資訊
- 資訊的完整性

### 人工評估標準

標準化的人工評估量表（5 分制）：

| 評分 | 標準 |
|------|------|
| 5 | 完全切題，精準回應問題核心 |
| 4 | 主要切題，有少量額外資訊 |
| 3 | 部分相關，回答問題的某些面向 |
| 2 | 僅觸及主題，未真正回答問題 |
| 1 | 完全離題 |

---

## 在 RAG 系統中的應用

### 雙重相關性評估

RAG（Retrieval-Augmented Generation）系統需要評估兩個層面的相關性：

| 層面 | 評估對象 | 指標 |
|------|----------|------|
| **檢索相關性** | 檢索到的文件與問題的相關程度 | Precision@K、MRR |
| **生成相關性** | 生成的答案與問題的相關程度 | Answer Relevancy |

### Context Relevance

Es et al. (2024) 提出 Context Relevance 指標，評估檢索內容的有效性：

$$\text{Context Relevance} = \frac{\text{相關句子數量}}{\text{總檢索句子數量}}$$

---

## 研究挑戰

### 相關性的主觀性

相關性判斷具有高度主觀性，不同評估者可能有不同判斷。Clarke et al. (2020) 的研究顯示，即使是專家評估者，相關性判斷的一致性也僅達中等水準（κ ≈ 0.4-0.6）。

### 語境依賴性

同一答案在不同語境下可能有不同的相關性。例如：

- 專家使用者期望技術細節
- 普通使用者期望淺顯說明

---

## 相關主題

- [準確率評估](metrics-accuracy.md)
- [真實性評估](metrics-faithfulness.md)

---

## 參考文獻

- Reimers, N., & Gurevych, I. (2019). "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"
- Es, S., et al. (2024). "RAGAS: Automated Evaluation of Retrieval Augmented Generation"
- Saracevic, T. (2007). "Relevance: A Review of the Literature and a Framework for Thinking on the Notion in Information Science"
