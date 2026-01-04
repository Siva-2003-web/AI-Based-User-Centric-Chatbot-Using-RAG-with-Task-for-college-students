"""
Vector Database Setup for College Assistant RAG System.
Initializes ChromaDB with 4 collections and loads indexed documents.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠ ChromaDB not installed. Install with: pip install chromadb")


class VectorDatabaseSetup:
    """Setup and manage vector database for college documents."""

    def __init__(self, chroma_dir: str = "./data/chroma"):
        self.chroma_dir = chroma_dir
        self.client = None
        self.collections = {}
        self.documents = {}

    def initialize_chroma(self) -> bool:
        """Initialize Chroma vector store with persistent storage."""
        if not CHROMA_AVAILABLE:
            print("❌ ChromaDB not available. Cannot proceed.")
            return False

        try:
            print(f"Initializing ChromaDB at: {self.chroma_dir}")
            
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=self.chroma_dir,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )
            print("✓ ChromaDB initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {e}")
            return False

    def create_collections(self) -> bool:
        """Create 4 separate collections for different document types."""
        if not self.client:
            print("❌ Chroma client not initialized")
            return False

        collection_configs = {
            "college_courses": {
                "description": "Course catalog with prerequisites, credits, instructors",
                "metadata_fields": ["course_code", "department", "level", "instructor"],
            },
            "faculty_info": {
                "description": "Faculty directory with contact, office hours, research areas",
                "metadata_fields": ["name", "department", "email", "office_location"],
            },
            "policies_procedures": {
                "description": "Student handbook policies, academic rules, procedures",
                "metadata_fields": ["section", "policy_type", "last_updated"],
            },
            "campus_facilities": {
                "description": "Campus facilities, hours, services, locations",
                "metadata_fields": ["facility_type", "location", "hours_open", "hours_close"],
            },
        }

        for collection_name, config in collection_configs.items():
            try:
                # Delete if exists to ensure clean slate
                try:
                    self.client.delete_collection(name=collection_name)
                except:
                    pass

                # Create collection
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={
                        "description": config["description"],
                        "hnsw:space": "cosine",
                    },
                )
                self.collections[collection_name] = collection
                print(f"✓ Created collection: {collection_name}")
            except Exception as e:
                print(f"❌ Error creating collection {collection_name}: {e}")
                return False

        return True

    def load_indexed_documents(self, jsonl_path: str = "data/indexed_documents.jsonl") -> bool:
        """Load documents from indexed JSONL file."""
        if not Path(jsonl_path).exists():
            print(f"❌ Indexed documents file not found: {jsonl_path}")
            return False

        try:
            with open(jsonl_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        doc_data = json.loads(line)
                        doc_id = doc_data["id"]
                        self.documents[doc_id] = doc_data

            print(f"✓ Loaded {len(self.documents)} documents from {jsonl_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            return False

    def categorize_documents(self) -> Dict[str, List[Dict]]:
        """Categorize documents into collections based on metadata."""
        categorized = {
            "college_courses": [],
            "faculty_info": [],
            "policies_procedures": [],
            "campus_facilities": [],
        }

        for doc_id, doc_data in self.documents.items():
            metadata = doc_data.get("metadata", {})
            category = metadata.get("category", "").lower()
            doc_type = metadata.get("document_type", "").lower()
            source = metadata.get("source_file", "").lower()

            # Route to appropriate collection
            if "course" in source or "catalog" in category or "course" in doc_type:
                categorized["college_courses"].append(doc_data)
            elif "faculty" in source or "faculty" in category or "department" in source:
                categorized["faculty_info"].append(doc_data)
            elif "handbook" in source or "policy" in category or "handbook" in doc_type:
                categorized["policies_procedures"].append(doc_data)
            elif "facilities" in source or "facilities" in category:
                categorized["campus_facilities"].append(doc_data)
            # Default: add to courses (largest collection)
            else:
                categorized["college_courses"].append(doc_data)

        return categorized

    def populate_collections(self) -> bool:
        """Populate collections with documents."""
        if not self.collections:
            print("❌ Collections not created")
            return False

        if not self.documents:
            print("❌ No documents loaded")
            return False

        print("\nPopulating collections...")
        categorized = self.categorize_documents()

        for collection_name, docs in categorized.items():
            if not docs:
                print(f"  ⚠ No documents for {collection_name}")
                continue

            collection = self.collections[collection_name]
            
            # Prepare data for upsert
            ids = [doc["id"] for doc in docs]
            documents = [doc["content"] for doc in docs]
            metadatas = [doc["metadata"] for doc in docs]

            try:
                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                )
                print(f"  ✓ {collection_name}: {len(docs)} documents upserted")
            except Exception as e:
                print(f"  ❌ Error upserting to {collection_name}: {e}")
                return False

        return True

    def test_filtering(self) -> None:
        """Test filtering and retrieval by department and metadata."""
        if not self.collections:
            print("❌ Collections not initialized")
            return

        print("\n" + "=" * 70)
        print("Vector Store Filtering Tests")
        print("=" * 70)

        # Test 1: Search for CS department courses
        print("\n[Test 1] Search CSE/Computer Science courses:")
        collection = self.collections["college_courses"]
        try:
            # Simple text query with where filter
            results = collection.query(
                query_texts=["Computer Science programming courses"],
                n_results=3,
                where={"department": {"$contains": "Computer"}},
            )
            
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0], 1):
                    print(f"  {i}. {doc[:100]}...")
            else:
                print("  No results (metadata filtering may need different syntax in Chroma)")
                # Fallback: simple query
                results = collection.query(
                    query_texts=["Computer Science programming"],
                    n_results=3,
                )
                if results and results["documents"]:
                    for i, doc in enumerate(results["documents"][0], 1):
                        print(f"  {i}. {doc[:100]}...")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # Test 2: Faculty information retrieval
        print("\n[Test 2] Search faculty information:")
        collection = self.collections["faculty_info"]
        try:
            results = collection.query(
                query_texts=["Alice Johnson office hours contact"],
                n_results=3,
            )
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0], 1):
                    print(f"  {i}. {doc[:100]}...")
            else:
                print("  No faculty results")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # Test 3: Policies retrieval
        print("\n[Test 3] Search policies and procedures:")
        collection = self.collections["policies_procedures"]
        try:
            results = collection.query(
                query_texts=["academic policies grading GPA requirements"],
                n_results=3,
            )
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0], 1):
                    print(f"  {i}. {doc[:100]}...")
            else:
                print("  No policy results")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # Test 4: Campus facilities
        print("\n[Test 4] Search campus facilities:")
        collection = self.collections["campus_facilities"]
        try:
            results = collection.query(
                query_texts=["library hours open close location"],
                n_results=3,
            )
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0], 1):
                    print(f"  {i}. {doc[:100]}...")
            else:
                print("  No facility results")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # Test 5: Cross-collection search (simulated)
        print("\n[Test 5] Collection statistics:")
        for collection_name, collection in self.collections.items():
            count = collection.count()
            print(f"  {collection_name}: {count} documents")

        print("\n" + "=" * 70)

    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics on all collections."""
        stats = {}
        for collection_name, collection in self.collections.items():
            stats[collection_name] = collection.count()
        return stats


def run_setup() -> None:
    """Main vector database setup."""
    print("\n" + "=" * 70)
    print("PHASE 3: Vector Database Setup")
    print("=" * 70)

    # Initialize
    setup = VectorDatabaseSetup()

    if not setup.initialize_chroma():
        print("\n❌ Failed to initialize ChromaDB. Cannot proceed.")
        print("   Install with: pip install chromadb")
        return

    # Create collections
    if not setup.create_collections():
        print("\n❌ Failed to create collections")
        return

    # Load documents
    if not setup.load_indexed_documents():
        print("\n❌ Failed to load documents")
        return

    # Populate collections
    if not setup.populate_collections():
        print("\n❌ Failed to populate collections")
        return

    # Get statistics
    print("\n" + "=" * 70)
    print("Collection Statistics:")
    print("=" * 70)
    stats = setup.get_collection_stats()
    for collection_name, count in stats.items():
        print(f"  {collection_name}: {count} documents")

    # Test retrieval
    setup.test_filtering()

    print("\n✅ Vector Database Setup Complete!")
    print(f"   Location: {setup.chroma_dir}")
    print("   Ready for RAG integration with FastAPI backend")


if __name__ == "__main__":
    run_setup()
