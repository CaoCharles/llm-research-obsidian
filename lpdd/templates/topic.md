# {{ topic_title }}

表現相關研究的彙整頁面。

## 最新論文
{{ first_paper_entry }}

## 所有相關論文

```dataview
LIST
FROM "Papers"
WHERE contains(tags, "{{ topic }}")
SORT date DESC
```

## 相關主題
- [[Topics/benchmark]]
- [[Topics/llm-as-judge]]

## 筆記
（手動補充主題相關的見解與總結）
