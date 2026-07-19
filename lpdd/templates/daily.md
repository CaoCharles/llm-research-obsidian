# {{ date }} 每日論文摘要

今日分析 **{{ paper_count }}** 篇 LLM 評測相關論文。

## 今日精選

{% for p in papers %}
### [{{ p.full_title }}](<../Papers/{{ p.link_name }}.md>)

`{{ p.category }}` · **相關度** {{ p.relevance_stars }} · **arXiv** {{ p.arxiv_id }}

#### 中文摘要

{{ p.abstract_zh }}

{% endfor %}

## 今日洞察
{% for highlight in highlights %}
- {{ highlight }}
{% endfor %}

---
> 由 LLM Paper Daily Digest 自動生成
