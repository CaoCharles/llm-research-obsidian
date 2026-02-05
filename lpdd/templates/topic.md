# {{ title }}

> {{ description }}

## 為什麼重要？

{{ importance }}

## 收錄標準

論文被收入此主題的原因：

{% for criteria in inclusion_criteria %}
- {{ criteria }}
{% endfor %}

## 研究方向

| 方向 | 說明 |
|------|------|
{% for direction in research_directions %}
| **{{ direction.name }}** | {{ direction.desc }} |
{% endfor %}

## 相關論文

{{ first_paper_entry }}

## 延伸閱讀

{% for topic in related_topics %}
- [[Topics/{{ topic }}|{{ topic }}]]
{% endfor %}

## 筆記

（手動補充主題相關的見解與總結）
