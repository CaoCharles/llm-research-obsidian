# RAGAS 評測框架

> RAG 系統的標準化評測方法論

## 概述

**RAGAS**（Retrieval-Augmented Generation Assessment）是 Es et al. (2024) 提出的 RAG 系統評測框架，提供系統化的評測指標和方法論，已成為 RAG 評測的事實標準。

---

## 理論基礎

### RAG 系統的評測挑戰

RAG 系統結合檢索與生成兩個組件，評測面臨獨特挑戰：

| 挑戰 | 說明 |
|------|------|
| **組件耦合** | 檢索錯誤與生成錯誤混合 |
| **評測複雜度** | 需同時評估多個維度 |
| **標準缺失** | 缺乏統一的評測標準 |

### 分離式評估

RAGAS 的核心理念是分離評估檢索和生成的品質：

```
[問題] → [檢索] → [上下文] → [生成] → [答案]
         ↓                    ↓
    檢索品質評估          生成品質評估
```

---

## 核心指標

### 生成品質指標

| 指標 | 定義 | 衡量對象 |
|------|------|----------|
| **Faithfulness** | 答案對上下文的忠實程度 | 幻覺程度 |
| **Answer Relevancy** | 答案與問題的相關程度 | 回答切題性 |

### 檢索品質指標

| 指標 | 定義 | 衡量對象 |
|------|------|----------|
| **Context Precision** | 相關上下文在檢索結果中的排序 | 精確性 |
| **Context Recall** | 標準答案可從上下文推導的程度 | 完整性 |

---

## 指標計算方法

### Faithfulness

評估答案中每個陳述是否可從上下文推導：

1. 將答案拆解為獨立陳述
2. 對每個陳述判斷是否有上下文支持
3. 計算有支持的陳述比例

$$\text{Faithfulness} = \frac{|V|}{|S|}$$

其中 $S$ 是所有陳述，$V$ 是可驗證的陳述。

### Answer Relevancy

評估答案與問題的語義相關性：

1. 從答案反向生成可能的問題
2. 計算生成問題與原始問題的語義相似度
3. 取平均相似度

### Context Precision

評估相關上下文的排序品質：

$$\text{Context Precision@K} = \frac{\sum_{k=1}^{K} (\text{Precision@k} \times v_k)}{\text{相關項目總數}}$$

其中 $v_k = 1$ 當第 $k$ 個上下文相關。

### Context Recall

評估標準答案是否可從上下文推導：

1. 將標準答案拆解為陳述
2. 對每個陳述判斷是否可從上下文推導
3. 計算可推導的比例

---

## 學術貢獻

### 與傳統指標的比較

Es et al. (2024) 的實驗顯示：

| 指標 | 與人類判斷相關性 |
|------|------------------|
| RAGAS Faithfulness | 0.67 |
| BLEU | 0.12 |
| ROUGE-L | 0.18 |

### 局限性討論

研究者指出的局限：
- 依賴 LLM 作為評審的偏見
- 對複雜推理的評估能力有限
- 跨語言應用需進一步驗證

---

## 應用建議

### 評測流程設計

1. **基線建立**：先評測基線系統
2. **維度分析**：識別主要問題維度
3. **迭代改進**：針對弱項優化
4. **持續監控**：部署後持續追蹤

### 閾值設定

| 應用場景 | Faithfulness | Answer Relevancy |
|----------|--------------|------------------|
| 高風險應用 | ≥ 0.9 | ≥ 0.85 |
| 一般業務 | ≥ 0.8 | ≥ 0.75 |
| 探索性應用 | ≥ 0.7 | ≥ 0.65 |

---

## 相關主題

- [DeepEval 指南](tools-deepeval.md)
- [Arize Phoenix 指南](tools-arize.md)
- [真實性評估](../Evaluation-Framework/metrics-faithfulness.md)

---

## 參考文獻

- Es, S., et al. (2024). "RAGAS: Automated Evaluation of Retrieval Augmented Generation"
- Saad-Falcon, J., et al. (2023). "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems"
