# LLM 評測知識庫

<p class="research-lead">系統化整理 LLM 評測策略、RAG 品質量測、基準測試、安全性與最新論文的實作知識庫。</p>

<div class="knowledge-stats" aria-label="知識庫統計">
  <div><strong>55</strong><span>篇論文</span></div>
  <div><strong>47</strong><span>個研究主題</span></div>
  <div><strong>4</strong><span>份每日摘要</span></div>
</div>

<div class="latest-digest">
  <div><span class="eyebrow">最新每日摘要</span><h2>2026-07-19</h2></div>
  <div><strong>1</strong><span>篇結構化論文分析</span></div>
  <a class="research-button" href="Daily/2026-07-19/">閱讀今日摘要 →</a>
</div>

## 快速開始

<div class="hub-grid">
  <a class="hub-card" href="Evaluation-Framework/"><span>📊</span><strong>評測策略與指標</strong><small>從準確率、真實性到 Responsible AI</small></a>
  <a class="hub-card" href="Benchmark-Governance/"><span>🧪</span><strong>基準測試與 RAG 工具</strong><small>RAGAS、DeepEval、Arize Phoenix 實作</small></a>
  <a class="hub-card" href="Security-RedTeam/"><span>🛡️</span><strong>安全性與紅隊演練</strong><small>Prompt Injection、Jailbreak 與 PII 防護</small></a>
  <a class="hub-card" href="Papers/"><span>📚</span><strong>搜尋論文庫</strong><small>按分類、標籤與關鍵字篩選</small></a>
</div>

## 最新論文

<div class="research-grid research-grid--latest">
<article class="research-card research-card--compact">
  <div class="research-card__meta"><span>2026-07-16</span><span>2607.15272</span></div>
  <h3><a href="Papers/%5B2607.15272%5D%20SciDiagramEdit%20-%20Learning%20to%20Edit%20Scientific%20Diagrams%20from%20Paper%20Revisions/">SciDiagramEdit: Learning to Edit Scientific Diagrams from Paper Revisions</a></h3>
  <p>在研究論文修訂過程中，編輯圖表是日常且耗時的工作：作者會重新標註元件、重排面板，並調整視覺風格。然而，根據自然語言指令自動完成這類編輯十分困難，因為 scientific figure 是一種高度密集的 infographic，包含示意圖、曲線圖、照片、圖說與箭頭等異質視覺元素，並依循嚴格的 visual grammar 來傳達特定論證。為此，我們提出 SciDiagramEdit，一個 benchmark 與 skill-evolu…</p>
  <div class="research-card__tags"><span class="research-category">benchmark</span><span class="research-tag">benchmark</span><span class="research-tag">agent-evaluation</span></div>
</article>
<article class="research-card research-card--compact">
  <div class="research-card__meta"><span>2026-02-05</span><span>2602.05656</span></div>
  <h3><a href="Papers/%5B2602.05656%5D%20Alignment%20Verifiability%20in%20Large%20Language%20Models%20-%20Normative%20Indistinguishabilit.../">Alignment Verifiability in Large Language Models: Normative Indistinguishability under Behavioral Evaluation</a></h3>
  <p>行為評估（behavioral evaluation）是評估大型語言模型對齊性的主流範式。在實踐中，對齊性是從有限評估協議（benchmark、紅隊測試套件或自動化管線）下的表現來推斷的，而觀察到的合規行為往往被視為潛在對齊屬性的證據。然而，從行為證據到潛在對齊性質的推論步驟通常是隱含的，鮮少作為一個獨立的推斷問題加以分析。本文正式研究此問題，將對齊評估框定為部分可觀測性（partial observability）下的可識別性問題，…</p>
  <div class="research-card__tags"><span class="research-category">Safety-Alignment</span><span class="research-tag">alignment</span><span class="research-tag">red-teaming</span></div>
</article>
<article class="research-card research-card--compact">
  <div class="research-card__meta"><span>2026-02-04</span><span>2602.04739</span></div>
  <h3><a href="Papers/%5B2602.04739%5D%20Alignment%20Drift%20in%20Multimodal%20LLMs%20-%20A%20Two-Phase%2C%20Longitudinal%20Evaluation%20of%20Har.../">Alignment Drift in Multimodal LLMs: A Two-Phase, Longitudinal Evaluation of Harm Across Eight Model Releases</a></h3>
  <p>多模態大型語言模型（MLLMs）正日益部署於真實系統中，但其在對抗性提示下的安全性仍未被充分探索。本研究透過由 26 名專業紅隊成員撰寫的 726 個對抗性提示組成的固定基準，進行兩階段的 MLLM 無害性評估。第一階段評估了 GPT-4o、Claude Sonnet 3.5、Pixtral 12B 和 Qwen VL Plus；第二階段評估其後繼版本（GPT-5、Claude Sonnet 4.5、Pixtral Large 和 Q…</p>
  <div class="research-card__tags"><span class="research-category">multimodal-safety</span><span class="research-tag">multimodal-safety</span><span class="research-tag">adversarial-attacks</span></div>
</article>
</div>

<p class="section-action"><a class="research-button research-button--secondary" href="Papers/">查看完整論文庫 →</a></p>

## NotebookLM 評測與安全指南

<div class="home-guide-panel" markdown>
這份由 NotebookLM 協助整理的完整指南，涵蓋企業級 LLM 品質驗證、評測指標與安全防禦策略。

[📥 下載完整評測與安全指南 (PDF)](assets/guides/LLM_Evaluation_and_Safety_Guide.pdf)

![LLM Evaluation Guide](assets/guides/LLM_Evaluation_and_Safety_Guide.pdf#navpanes=0&toolbar=0){ type=application/pdf class="home-guide-embed" }
</div>

!!! tip "詢問 AI 助教"
    點擊右下角聊天按鈕，可以詢問評測方法、RAG 工具、安全測試與論文重點。
