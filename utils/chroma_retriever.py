"""
Enhanced Retriever using ChromaDB vector store.
Supports collection-specific queries with metadata filtering.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class ChromaRetriever:
    """Retriever using ChromaDB vector store with multiple collections."""

    def __init__(self, chroma_dir: str = "./data/chroma"):
        self.chroma_dir = chroma_dir
        self.client = None
        self.collections = {}
        self.initialize()

    def initialize(self) -> bool:
        """Initialize Chroma client and load collections."""
        try:
            self.client = chromadb.PersistentClient(
                path=self.chroma_dir,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=False,
                ),
            )
            
            # Load existing collections
            collection_names = ["college_courses", "faculty_info", "policies_procedures", "campus_facilities"]
            for name in collection_names:
                try:
                    self.collections[name] = self.client.get_collection(name=name)
                except:
                    pass

            if self.collections:
                print(f"✓ Loaded {len(self.collections)} collections from Chroma")
                return True
            else:
                print("⚠ No collections found. Run: python -m utils.setup_vectordb")
                return False
        except Exception as e:
            print(f"❌ Error initializing Chroma: {e}")
            return False

    def search_collection(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        where_filter: Optional[Dict] = None,
    ) -> List[Dict]:
        """Search a specific collection."""
        if collection_name not in self.collections:
            print(f"⚠ Collection {collection_name} not found")
            return []

        collection = self.collections[collection_name]
        try:
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
            )

            # Format results
            retrieved = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    # Convert distance to similarity (0-1, higher = better)
                    similarity = 1 - (distance / 2) if distance else 0.5
                    
                    retrieved.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "collection": collection_name,
                    })
            return retrieved
        except Exception as e:
            print(f"⚠ Error searching {collection_name}: {e}")
            return []

    def search_all(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, List[Dict]]:
        """Search across all collections."""
        results = {}
        for collection_name in self.collections:
            results[collection_name] = self.search_collection(query, collection_name, top_k)
        return results

    def format_results(self, results: List[Dict], max_chars: int = 120) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."

        output = f"\n{'='*70}\nRetrieved {len(results)} documents:\n{'='*70}\n"
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            similarity = result.get("similarity", 0)
            collection = result.get("collection", "unknown")
            content = result["content"][:max_chars].replace("\n", " ")
            
            output += f"\n[{i}] {collection} | Similarity: {similarity:.3f}\n"
            if metadata:
                meta_str = " | ".join(f"{k}: {v}" for k, v in list(metadata.items())[:3])
                output += f"    Metadata: {meta_str}\n"
            output += f"    Content: {content}...\n"
        
        output += f"\n{'='*70}\n"
        return output


def run_comprehensive_tests() -> None:
    """Run comprehensive vector database tests."""
    print("\n" + "=" * 70)
    print("PHASE 3: Vector Database - Comprehensive Testing")
    print("=" * 70)

    retriever = ChromaRetriever()

    if not retriever.client:
        print("❌ Failed to initialize retriever")
        return

    print("\nTesting collection-specific queries...\n")

    # Test 1: Computer Science courses
    print("[Test 1] Search Computer Science courses:")
    results = retriever.search_collection(
        query="Computer Science programming courses algorithms",
        collection_name="college_courses",
        top_k=3,
    )
    print(retriever.format_results(results))

    # Test 2: Faculty with department filter
    print("[Test 2] Search Mathematics faculty:")
    results = retriever.search_collection(
        query="Mathematics faculty linear algebra calculus",
        collection_name="faculty_info",
        top_k=3,
    )
    print(retriever.format_results(results))

    # Test 3: Academic policies
    print("[Test 3] Search academic policies and grading:")
    results = retriever.search_collection(
        query="academic policies grading GPA requirements",
        collection_name="policies_procedures",
        top_k=3,
    )
    print(retriever.format_results(results))

    # Test 4: Campus facilities
    print("[Test 4] Search library facilities and hours:")
    results = retriever.search_collection(
        query="library hours location study rooms",
        collection_name="campus_facilities",
        top_k=3,
    )
    print(retriever.format_results(results))

    # Test 5: Cross-collection search
    print("[Test 5] Cross-collection search for registration:")
    all_results = retriever.search_all(
        query="course registration enrollment deadline",
        top_k=3,
    )
    
    print("Results by collection:")
    for collection_name, results in all_results.items():
        if results:
            print(f"\n  {collection_name} ({len(results)} results):")
            for i, result in enumerate(results[:2], 1):  # Show top 2 from each
                content = result["content"][:80].replace("\n", " ")
                print(f"    {i}. {content}...")

    # Test 6: Department-specific filtering
    print("\n[Test 6] CSE department courses (advanced filtering):")
    # Note: Chroma metadata filtering requires $eq, not $contains
    results = retriever.search_collection(
        query="CSE courses programming data structures",
        collection_name="college_courses",
        top_k=3,
        where_filter={"department": {"$eq": "Computer Science"}},
    )
    if results:
        print(retriever.format_results(results))
    else:
        print("  (Querying without strict filter...)")
        results = retriever.search_collection(
            query="Computer Science data structures algorithms",
            collection_name="college_courses",
            top_k=3,
        )
        print(retriever.format_results(results))

    # Collection statistics
    print("\n[Collection Statistics]:")
    print("=" * 70)
    for collection_name, collection in retriever.collections.items():
        count = collection.count()
        print(f"  {collection_name}: {count} documents")
    print("=" * 70)

    print("\n✅ Vector Database Tests Complete!")
    print("   Ready for RAG integration with FastAPI backend")


if __name__ == "__main__":
    run_comprehensive_tests()
