# {{ date }} 論文摘要

今日分析 **{{ paper_count }}** 篇 LLM 評測相關論文。

## 今日論文

| 分類 | 論文 | 相關度 |
|------|------|--------|
{% for p in papers %}
| `[{{ p.category }}]` | [[{{ p.link_name }}\|{{ p.title }}]] | {{ p.relevance_stars }} |
{% endfor %}

## 論文摘要

{% for p in papers %}
### `[{{ p.category }}]` [[{{ p.link_name }}\|{{ p.title }}]]

{{ p.abstract_zh }}

{% endfor %}

## 重點發現
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}

---
> 由 LLM Paper Daily Digest 自動生成
