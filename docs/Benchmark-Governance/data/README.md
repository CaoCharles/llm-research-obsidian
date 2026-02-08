# 金融 RAG 共用測試資料

## 文件來源

- 文件名稱：Federal Reserve - Financial Stability Report (Nov 2021)
- 原始連結：https://www.federalreserve.gov/publications/files/financial-stability-report-20211108.pdf
- 下載檔案：`financial-stability-report-20211108.pdf`
- 文字抽取檔：`financial-stability-report-20211108.txt`

## 用途

這份資料用於三套評測工具（RAGAS、DeepEval、Arize Phoenix）的橫向比較，確保：

1. 使用同一份語料庫。
2. 使用同一批問題集。
3. 使用同一個簡易 RAG baseline。

## 共用問題集

- 檔案：`finance-rag-benchmark.json`
- 欄位說明：
  - `id`: 測試案例編號
  - `question`: 使用者問題
  - `ground_truth`: 參考答案
  - `topic`: 題目主題
  - `difficulty`: 難度標記（easy/medium）

