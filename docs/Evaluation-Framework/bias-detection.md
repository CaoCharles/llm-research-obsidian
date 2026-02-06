# 偏見檢測與緩解

> 識別並減少 LLM 中的系統性偏見

## 概述

大型語言模型從大規模網際網路文本中學習，不可避免地吸收並可能放大社會中存在的偏見。偏見檢測與緩解是確保 AI 公平性的關鍵研究領域。

---

## 偏見的分類

### 依來源分類

Mehrabi et al. (2021) 將 ML 偏見分類為：

| 類型 | 來源 | 範例 |
|------|------|------|
| **歷史偏見** | 資料反映過去的不平等 | 招聘資料中女性比例偏低 |
| **代表性偏見** | 某群體在資料中代表不足 | 少數族裔的圖像較少 |
| **測量偏見** | 代理變數與目標概念不對應 | 用郵遞區號代理收入 |
| **評估偏見** | 評測標準本身帶有偏見 | 以歐美文化為標準 |

### 依表現形式分類

Blodgett et al. (2020) 針對 NLP 系統的偏見分類：

| 類型 | 定義 |
|------|------|
| **刻板印象** | 對群體的過度概括假設 |
| **貶低性語言** | 對特定群體使用負面語彙 |
| **排斥性傷害** | 系統對某群體效能較差 |
| **品質差異** | 對不同群體的服務品質不同 |

---

## 檢測方法

### 反事實測試

Garg et al. (2019) 提出反事實公平測試：

1. 設計包含敏感屬性的句子模板
2. 僅替換敏感屬性（如性別）
3. 比較模型輸出的差異

範例模板：
- 「The {gender} doctor is skilled.」
- 「The {race} student is intelligent.」

### 詞彙關聯測試

**WEAT（Word Embedding Association Test）**

Caliskan et al. (2017) 仿照心理學的隱性關聯測試（IAT）設計：

- 計算目標詞彙與屬性詞彙的嵌入相似度
- 比較不同群體詞彙與正面/負面屬性的關聯

**SEAT（Sentence Encoder Association Test）**

May et al. (2019) 將 WEAT 擴展至句子層級。

### 偏見基準測試

| 基準 | 內容 | 提出者 |
|------|------|--------|
| **CrowS-Pairs** | 刻板印象配對測試 | Nangia et al. (2020) |
| **StereoSet** | 跨多維度的刻板印象 | Nadeem et al. (2021) |
| **WinoBias** | 性別偏見指代消解 | Zhao et al. (2018) |
| **BBQ** | 問答中的偏見 | Parrish et al. (2022) |

---

## 緩解策略

### 訓練前策略

| 策略 | 說明 | 研究 |
|------|------|------|
| **資料平衡** | 確保各群體代表性 | Dixon et al. (2018) |
| **資料增強** | 生成反事實樣本 | Lu et al. (2020) |
| **資料過濾** | 移除高偏見內容 | Gehman et al. (2020) |

### 訓練中策略

| 策略 | 說明 | 研究 |
|------|------|------|
| **對抗訓練** | 使模型無法預測敏感屬性 | Zhang et al. (2018) |
| **約束優化** | 在損失函數中加入公平約束 | Kamishima et al. (2012) |
| **正則化** | 懲罰對敏感屬性的依賴 | Beutel et al. (2017) |

### 訓練後策略

| 策略 | 說明 | 研究 |
|------|------|------|
| **投影方法** | 移除嵌入中的敏感方向 | Bolukbasi et al. (2016) |
| **提示工程** | 指示模型避免偏見 | Ganguli et al. (2023) |
| **輸出過濾** | 後處理移除偏見內容 | Xu et al. (2021) |

---

## 研究挑戰

### 偏見的隱蔽性

Guo et al. (2022) 指出，顯式去偏見方法可能只是隱藏而非消除偏見：

- 模型可能學會避免直接表達偏見
- 但在隱式推理中仍保留偏見

### 去偏見的副作用

Blodgett et al. (2021) 警告過度去偏見可能：

- 降低模型對少數群體語言的理解
- 損害文化表達的多樣性

---

## 相關主題

- [公平性驗收標準](fairness.md)
- [可解釋性要求](explainability.md)

---

## 參考文獻

- Mehrabi, N., et al. (2021). "A Survey on Bias and Fairness in Machine Learning"
- Blodgett, S. L., et al. (2020). "Language (Technology) is Power: A Critical Survey of 'Bias' in NLP"
- Caliskan, A., et al. (2017). "Semantics derived automatically from language corpora contain human-like biases"
