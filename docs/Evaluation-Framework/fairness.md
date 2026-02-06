# 公平性驗收標準

> 確保 AI 系統對所有使用者群體一視同仁

## 定義

**公平性**（Fairness）指 AI 系統在處理不同群體時，不會基於敏感屬性（如性別、種族、年齡）產生不合理的差異對待。這是 Responsible AI 的核心要求之一。

---

## 理論基礎

### 公平性的哲學基礎

AI 公平性研究植根於政治哲學與法學傳統：

| 概念 | 來源 | 在 AI 中的應用 |
|------|------|----------------|
| **形式公平** | 亞里士多德 | 相似案例同等對待 |
| **實質公平** | 羅爾斯 | 關注結果分配的公正 |
| **程序公平** | 法學傳統 | 決策過程的公正 |

### 公平性的數學定義

Barocas et al. (2019) 將公平性指標分為三大類：

**1. 群體公平（Group Fairness）**

確保各人口群體的統計結果相等：

| 指標 | 定義 |
|------|------|
| **人口均等** | P(Ŷ=1\|A=0) = P(Ŷ=1\|A=1) |
| **機會均等** | P(Ŷ=1\|Y=1,A=0) = P(Ŷ=1\|Y=1,A=1) |
| **結果均等** | TPR 和 FPR 同時相等 |

**2. 個體公平（Individual Fairness）**

相似個體應獲得相似對待（Dwork et al., 2012）：

> 若 d(x, x') ≤ ε，則 d(f(x), f(x')) 應相應地小

**3. 反事實公平（Counterfactual Fairness）**

若改變敏感屬性不影響預測結果（Kusner et al., 2017）

---

## 評測方法

### 分層分析

對每個敏感群體分別計算模型效能：

| 分析維度 | 說明 |
|----------|------|
| 性別 | 男/女/其他 |
| 年齡 | 各年齡段 |
| 地區 | 不同地理區域 |
| 語言 | 不同語言使用者 |

### 差異度量

Corbett-Davies & Goel (2018) 提出的差異度量：

| 度量 | 計算方式 |
|------|----------|
| **差異比** | max(P₁, P₂) / min(P₁, P₂) |
| **絕對差異** | \|P₁ - P₂\| |
| **標準化差異** | (P₁ - P₂) / σ |

### 交叉性分析

Buolamwini & Gebru (2018) 的研究強調交叉性的重要性：

- 單獨檢視性別或種族可能遺漏問題
- 「黑人女性」群體可能受到獨特的不公平對待
- 需要進行多屬性交叉分析

---

## 驗收標準建議

### 通過閾值

| 風險等級 | 最大允許差異 | 適用場景 |
|----------|--------------|----------|
| 高風險 | < 5% | 醫療、法律、金融 |
| 中風險 | < 10% | 一般商業應用 |
| 低風險 | < 20% | 娛樂、建議性功能 |

### 驗收清單

- 所有主要群體的效能差異是否在閾值內？
- 是否進行了交叉性分析？
- 是否有群體的拒絕率異常偏高？
- 高風險決策是否有人工復核機制？

---

## 學術挑戰

### 不可能定理

Kleinberg et al. (2017) 與 Chouldechova (2017) 獨立證明：

> 除特殊情況外，calibration、false positive parity 和 false negative parity 無法同時滿足。

這意味著組織需要根據具體場景做出價值選擇。

### 公平性與準確率的權衡

Corbett-Davies et al. (2017) 的研究顯示：

- 強制公平約束可能降低整體預測準確率
- 權衡的幅度取決於群體間基礎率的差異

---

## 相關主題

- [偏見檢測與緩解](bias-detection.md)
- [Responsible AI 標準](responsible-ai.md)

---

## 參考文獻

- Barocas, S., et al. (2019). "Fairness and Machine Learning"
- Dwork, C., et al. (2012). "Fairness through Awareness"
- Buolamwini, J., & Gebru, T. (2018). "Gender Shades: Intersectional Accuracy Disparities in Commercial Gender Classification"
- Kleinberg, J., et al. (2017). "Inherent Trade-Offs in the Fair Determination of Risk Scores"
