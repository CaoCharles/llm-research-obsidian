from unittest.mock import patch

from retrieval import KnowledgeRetriever, _terms


DOCUMENTS = [
    {
        "title": "RAGAS 完整教學",
        "url": "https://example.test/ragas/",
        "content": "# RAGAS\n\nRAGAS 使用 faithfulness 與 answer relevancy 評估 RAG 系統。",
    },
    {
        "title": "Prompt Injection 防禦",
        "url": "https://example.test/prompt-injection/",
        "content": "# Prompt Injection\n\n應隔離不可信的外部內容並實施輸出驗證。",
    },
]


def test_terms_support_mixed_chinese_and_english():
    terms = _terms("如何評估 RAGAS？")

    assert "ragas" in terms
    assert "評估" in terms


def test_retrieve_returns_relevant_unique_pages():
    retriever = KnowledgeRetriever("https://example.test/content.json")

    with patch.object(retriever, "_fetch_documents", return_value=DOCUMENTS):
        results = retriever.retrieve("RAGAS 的 faithfulness 如何評估？", top_k=2)

    assert results
    assert results[0].title == "RAGAS 完整教學"
    assert results[0].url == "https://example.test/ragas/"
    assert len({result.url for result in results}) == len(results)


def test_retrieve_reuses_cached_documents():
    retriever = KnowledgeRetriever("https://example.test/content.json")

    with patch.object(retriever, "_fetch_documents", return_value=DOCUMENTS) as fetch:
        retriever.retrieve("RAGAS")
        retriever.retrieve("Prompt Injection")

    fetch.assert_called_once()


def test_distinctive_title_term_beats_index_page_mention():
    retriever = KnowledgeRetriever("https://example.test/content.json")
    documents = [
        {
            "title": "論文庫",
            "url": "https://example.test/papers/",
            "content": "SciDiagramEdit 是今日最新論文。",
        },
        {
            "title": "SciDiagramEdit: Learning to Edit Scientific Diagrams",
            "url": "https://example.test/papers/scidiagramedit/",
            "content": "這篇研究提出科學圖表編輯 benchmark。",
        },
    ]

    with patch.object(retriever, "_fetch_documents", return_value=documents):
        results = retriever.retrieve("今天最新的 SciDiagramEdit 論文重點", top_k=2)

    assert results[0].url.endswith("/papers/scidiagramedit/")


def test_low_scoring_sources_are_excluded():
    retriever = KnowledgeRetriever("https://example.test/content.json")
    documents = [
        {
            "title": "SciDiagramEdit",
            "url": "https://example.test/scidiagramedit/",
            "content": "SciDiagramEdit scientific diagram benchmark revision editing.",
        },
        {
            "title": "Unrelated paper",
            "url": "https://example.test/unrelated/",
            "content": "This paper mentions editing once but studies another subject.",
        },
    ]

    with patch.object(retriever, "_fetch_documents", return_value=documents):
        results = retriever.retrieve("SciDiagramEdit editing benchmark", top_k=5)

    assert [result.url for result in results] == [
        "https://example.test/scidiagramedit/"
    ]


def test_expired_cache_falls_back_to_stale_documents():
    retriever = KnowledgeRetriever("https://example.test/content.json")

    with patch.object(retriever, "_fetch_documents", return_value=DOCUMENTS):
        first_results = retriever.retrieve("RAGAS")

    retriever._loaded_at = 0
    with patch.object(
        retriever,
        "_fetch_documents",
        side_effect=TimeoutError("temporary outage"),
    ):
        stale_results = retriever.retrieve("RAGAS")

    assert stale_results[0].url == first_results[0].url
