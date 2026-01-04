"""
Step 6: Retrieval System tests using Chroma collections with metadata filters.
"""

from typing import Dict, List

from utils.chroma_retriever import ChromaRetriever


def _flatten_results(all_results: Dict[str, List[Dict]]) -> List[Dict]:
    """Combine cross-collection results into a single ranked list."""
    combined: List[Dict] = []
    for collection, items in all_results.items():
        for item in items:
            combined.append({**item, "collection": collection})
    return sorted(combined, key=lambda r: r.get("similarity", 0), reverse=True)


def _run_single_query(
    retriever: ChromaRetriever,
    title: str,
    query: str,
    collection: str,
    where_filter: Dict | None,
    top_k: int = 3,
) -> None:
    print(f"\n[Query] {title}")
    print(f"Text   : {query}")
    if where_filter:
        print(f"Filter : {where_filter}")

    results = retriever.search_collection(
        query=query,
        collection_name=collection,
        top_k=top_k,
        where_filter=where_filter,
    )

    if not results:
        print("  No direct hits in collection; trying cross-collection fallback...")
        results = _flatten_results(retriever.search_all(query, top_k=top_k))

    if results:
        print(retriever.format_results(results, max_chars=220))
    else:
        print("  No results found across collections.\n")


def run_step6_tests() -> None:
    """Execute Step 6 retrieval checks with semantic search and metadata filters."""
    print("\n" + "=" * 70)
    print("Step 6: Retrieval System — College Queries")
    print("=" * 70)

    retriever = ChromaRetriever()
    if not retriever.collections:
        print("❌ No collections available. Run: python -m utils.setup_vectordb")
        return

    scenarios = [
        {
            "title": "Who is the HOD of Computer Science?",
            "query": "Who is the head of department for Computer Science?",
            "collection": "faculty_info",
            "where": {"department": {"$eq": "Computer Science"}},
        },
        {
            "title": "What is the syllabus for Database Management?",
            "query": "What is the syllabus for the Database Management course?",
            "collection": "college_courses",
            "where": {"category": {"$eq": "catalogs"}},
        },
        {
            "title": "When is the mid-term exam for AI course?",
            "query": "When is the mid-term exam for the Artificial Intelligence course?",
            "collection": "college_courses",
            "where": {"department": {"$eq": "Computer Science"}},
        },
    ]

    for scenario in scenarios:
        _run_single_query(
            retriever=retriever,
            title=scenario["title"],
            query=scenario["query"],
            collection=scenario["collection"],
            where_filter=scenario.get("where"),
            top_k=3,
        )


if __name__ == "__main__":
    run_step6_tests()
