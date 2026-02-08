# 評測工具 Notebook 實作

這一頁集中放置可直接複製使用的教學 Notebook。  
目前包含三份單工具教學與一份跨工具統整版，方便新人快速上手與團隊回歸測試。

美國金融文件（單工具教學共用）：

1. PDF：`/Benchmark-Governance/data/financial-stability-report-20211108.pdf`
2. 題庫：`/Benchmark-Governance/data/finance-rag-benchmark.json`

台灣金融文件（跨工具統整版共用）：

1. PDF：`/Benchmark-Governance/data/taiwan-financial-stability-report-2025.pdf`
2. 題庫：`/Benchmark-Governance/data/taiwan-finance-rag-benchmark-2025.json`
3. 結果輸出：`/Benchmark-Governance/data/results/`

## 下載與開啟

1. RAGAS：`/Benchmark-Governance/notebooks/ragas-tutorial.ipynb`
2. DeepEval：`/Benchmark-Governance/notebooks/deepeval-tutorial.ipynb`
3. Arize Phoenix：`/Benchmark-Governance/notebooks/arize-phoenix-tutorial.ipynb`
4. 跨工具統整版（台灣金融文件）：`/Benchmark-Governance/notebooks/taiwan-finance-cross-tool-eval.ipynb`
5. 橫向比較導讀：`/Benchmark-Governance/cross-tool-rag-benchmark.md`

## 建議啟動方式（uv）

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -U jupyter ipykernel
jupyter lab
```

打開對應 `ipynb` 後，請選擇你建立的 kernel。
