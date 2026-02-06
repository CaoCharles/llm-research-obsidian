# 對抗性樣本

> 測試模型對惡意或誤導性輸入的魯棒性

## 概述

**對抗性樣本**（Adversarial Examples）是經過精心設計，旨在誤導模型產生錯誤輸出的輸入。Goodfellow et al. (2015) 的開創性研究揭示了深度學習模型對細微擾動的脆弱性，這一發現在 NLP 領域同樣適用。

---

## 理論基礎

### 對抗性攻擊的定義

形式化地，對抗性攻擊尋找：

$$x' = x + \delta$$

使得：
- $\|δ\|$ 足夠小（人類難以察覺）
- $f(x') \neq f(x)$（模型預測改變）

### 攻擊類型

| 類型 | 定義 | 研究代表 |
|------|------|----------|
| **白盒攻擊** | 已知模型結構和參數 | Ebrahimi et al. (2018) |
| **黑盒攻擊** | 僅能查詢模型輸出 | Jin et al. (2020) |
| **遷移攻擊** | 利用一個模型的弱點攻擊另一個 | Wallace et al. (2019) |

---

## NLP 對抗攻擊研究

### 字符層面攻擊

Ebrahimi et al. (2018) 的 HotFlip 方法：

| 擾動類型 | 說明 |
|----------|------|
| 字符替換 | a → α（視覺相似） |
| 字符插入 | password → p​assword（零寬字符）|
| 字符刪除 | weather → weathr |
| 字符交換 | tried → tired |

### 詞彙層面攻擊

Jin et al. (2020) 的 TextFooler 方法：

1. 識別對預測影響最大的詞彙
2. 以語義相近的詞彙替換
3. 保持語法正確性和語義一致性

### 句子層面攻擊

Iyyer et al. (2018) 的句法擾動：

- 主動語態 ↔ 被動語態
- 調整修飾語位置
- 改變從句結構

---

## 對 LLM 的特殊攻擊

### Prompt Injection

Perez & Ribeiro (2022) 描述的注入攻擊：

- 在使用者輸入中嵌入惡意指令
- 目標是覆蓋系統的原始指令
- 詳見：[Prompt Injection 防禦](../Security-RedTeam/defense-prompt-injection.md)

### 對抗性後綴

Zou et al. (2023) 的 GCG（Greedy Coordinate Gradient）攻擊發現：

- 附加特定優化的字串可繞過安全對齊
- 這些後綴對人類無意義
- 攻擊可跨模型遷移

### 間接注入

Greshake et al. (2023) 描述的資料中毒：

- 攻擊者在外部資料來源植入惡意指令
- 當 RAG 系統檢索這些資料時被激活
- 使用者完全不知情

---

## 評估方法

### 攻擊成功率

$$\text{ASR} = \frac{\text{成功攻擊的樣本數}}{\text{總攻擊嘗試數}}$$

### 擾動幅度

衡量對抗樣本與原始輸入的差異：

| 度量 | 適用情境 |
|------|----------|
| 編輯距離 | 字符/詞彙層面 |
| 語義相似度 | 確保語義保持 |
| 人類察覺率 | 擾動隱蔽性 |

### 魯棒性準確率

在對抗樣本上的模型準確率：

$$\text{Robust Acc} = \frac{\text{對抗樣本中正確預測數}}{\text{對抗樣本總數}}$$

---

## 防禦研究

| 防禦類型 | 方法 | 研究 |
|----------|------|------|
| **訓練時** | 對抗訓練 | Zhu et al. (2020) |
| **推理時** | 輸入淨化 | Wang et al. (2021) |
| **模型層面** | 認證防禦 | Jia et al. (2019) |

---

## 相關主題

- [邊緣案例設計](edge-cases.md)
- [安全性與紅隊演練](../Security-RedTeam/index.md)

---

## 參考文獻

- Goodfellow, I. J., et al. (2015). "Explaining and Harnessing Adversarial Examples"
- Jin, D., et al. (2020). "Is BERT Really Robust? A Strong Baseline for Natural Language Attack on Text Classification and Entailment"
- Zou, A., et al. (2023). "Universal and Transferable Adversarial Attacks on Aligned Language Models"
