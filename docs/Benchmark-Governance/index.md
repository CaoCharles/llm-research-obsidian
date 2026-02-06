# 基準測試與數據治理

> 建立和維護高品質評測資料集的方法論與實務指南

## 概述

基準測試（Benchmark）是 LLM 評測的基石。Liang et al. (2023) 指出：「沒有高品質的基準測試，就無法客觀比較不同模型的能力。」本章節探討基準測試的設計原則、資料治理策略，以及主流評測工具的應用。

---

## 基準測試的學術意義

### 推動領域發展

經典基準測試對 NLP 領域的推動作用：

| 基準 | 年份 | 貢獻 |
|------|------|------|
| **GLUE/SuperGLUE** | 2018/2019 | 統一 NLU 評測標準 |
| **SQuAD** | 2016 | 推動閱讀理解研究 |
| **MMLU** | 2021 | 大規模多領域知識評測 |
| **GSM8K** | 2021 | 數學推理能力基準 |
| **HumanEval** | 2021 | 代碼生成評測標準 |

### 基準測試的演進

隨著模型能力提升，基準測試也不斷演進：

| 階段 | 特點 | 代表基準 |
|------|------|----------|
| **早期** | 單一任務、自動評分 | WMT、SQuAD |
| **中期** | 多任務聚合 | GLUE、SuperGLUE |
| **現代** | 開放生成、人類評估 | Chatbot Arena、MT-Bench |

---

## 核心議題

### 測試集設計

高品質測試集的建立與維護：

- [黃金測試集管理](golden-testset.md) - 標準測試集的設計原則
- [數據集生命週期](dataset-lifecycle.md) - 測試集的維護與更新

### 覆蓋率設計

確保測試涵蓋所有重要場景：

- [業務關鍵路徑覆蓋](critical-path.md) - 核心功能的測試覆蓋
- [邊緣案例設計](edge-cases.md) - 極端與異常情況測試
- [對抗性樣本](adversarial-samples.md) - 魯棒性測試

### 評測工具

主流開源評測框架：

- [RAGAS](tools-ragas.md) - RAG 系統評測框架
- [DeepEval](tools-deepeval.md) - 通用 LLM 評測工具
- [Arize Phoenix](tools-arize.md) - LLM 可觀測性平台

---

## 基準測試的挑戰

### 資料污染

Sainz et al. (2023) 指出，測試資料洩入訓練集是嚴重問題：

- 模型可能「記住」測試題目
- 高分可能不反映真實能力
- 跨基準比較失去意義

### 飽和問題

許多經典基準已接近飽和：

| 基準 | 人類表現 | 最佳模型 | 狀態 |
|------|----------|----------|------|
| SQuAD 2.0 | 86.8 | 93.0 | 飽和 |
| GLUE | 87.1 | 91.3 | 飽和 |
| SuperGLUE | 89.8 | 91.4 | 接近飽和 |

### 代表性不足

現有基準可能無法反映真實應用場景（Bowman & Dahl, 2021）：

- 偏向學術任務
- 西方語言中心
- 缺乏長期互動評估

---

## 理論框架

### 評測有效性

借鏡心理測量學的評測設計原則：

| 概念 | 應用 |
|------|------|
| **內容效度** | 測試是否涵蓋目標能力的所有面向 |
| **建構效度** | 測試是否真正測量目標能力 |
| **預測效度** | 測試成績是否預測真實表現 |

### 動態評測

Zhu et al. (2023) 提出動態基準測試的概念：

- 定期更新測試題目
- 從真實應用中收集新案例
- 減少資料污染風險

---

## 相關主題

- [評測策略與框架設計](../Evaluation-Framework/index.md)
- [安全性與紅隊演練](../Security-RedTeam/index.md)

---

## 參考文獻

- Liang, P., et al. (2023). "Holistic Evaluation of Language Models (HELM)"
- Sainz, O., et al. (2023). "NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination for each Benchmark"
- Bowman, S. R., & Dahl, G. (2021). "What Will it Take to Fix Benchmarking in Natural Language Understanding?"
