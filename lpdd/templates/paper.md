---
arxiv_id: "{{ arxiv_id }}"
title: "{{ title }}"
date: {{ date }}
authors:
{% for author in authors %}
  - {{ author }}
{% endfor %}
institution: "{{ institution }}"
tags:
{% for tag in tags %}
  - {{ tag }}
{% endfor %}
category: "{{ category }}"
relevance: {{ relevance }}
status: unread
aliases:
  - "{{ safe_title }}"
---

# {{ title }}

## 連結
- 📄 [arXiv]({{ arxiv_url }})
- 📥 [PDF]({{ pdf_url }})
{% if pdf_embed %}
- 📎 本地 PDF: [[{{ pdf_filename }}]]
{% endif %}

## 摘要（中文翻譯）

{{ abstract_zh }}

{% if pdf_embed %}
## 論文預覽

![[{{ pdf_filename }}#page=1]]

{% endif %}
## 問題背景

{{ problem_statement }}

## 解決方案

{{ proposed_solution }}

## 核心貢獻
{% for contribution in core_contributions %}
{{ loop.index }}. {{ contribution }}
{% endfor %}

## 技術方法

{{ methodology }}

## 關鍵結果

{{ key_results }}

## 對我們的啟發
{% for insight in insights %}
- [ ] {{ insight }}
{% endfor %}

{% if limitations %}
## 限制與未來工作

{{ limitations }}
{% endif %}

## 相關主題
{% for topic in related_topics %}
- [[Topics/{{ topic }}|{{ topic }}]]
{% endfor %}

## 筆記
（手動補充）
