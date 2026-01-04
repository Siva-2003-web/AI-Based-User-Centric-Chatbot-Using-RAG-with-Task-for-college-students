"""
Ingestion pipeline for college documents -> chunks -> embeddings -> vector store.
Handles CSVs, text files, and PDFs; creates chunks with metadata and deduplication.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import hashlib
import json

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False


class Document:
    """Represents a document chunk with metadata."""

    def __init__(
        self,
        content: str,
        source_file: str,
        document_type: str,
        section: str = "",
        chunk_index: int = 0,
        last_updated: str = None,
        category: str = "",
        department: str = "",
        confidentiality: str = "public",
    ):
        self.content = content
        self.source_file = source_file
        self.document_type = document_type
        self.section = section
        self.chunk_index = chunk_index
        self.last_updated = last_updated or datetime.now().isoformat()
        self.category = category  # course, policy, faculty, facilities, financial, calendar
        self.department = department  # Computer Science, Mathematics, etc.
        self.confidentiality = confidentiality  # public, restricted, internal
        self.embedding: Optional[List[float]] = None
        # Unique ID based on content hash for deduplication
        self.id = hashlib.md5(f"{source_file}_{chunk_index}_{content[:50]}".encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": {
                "source_file": self.source_file,
                "document_type": self.document_type,
                "section": self.section,
                "chunk_index": self.chunk_index,
                "last_updated": self.last_updated,
                "category": self.category,
                "department": self.department,
                "confidentiality": self.confidentiality,
            },
        }


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks (by token approximation)."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def load_csv_documents(csv_path: Path) -> List[Document]:
    """Load CSV and convert rows to documents with category metadata."""
    documents = []
    # Determine category and department from file path
    category = csv_path.parent.name  # catalogs, faculty, facilities, fees_scholarships, calendar
    department = infer_department_from_path(csv_path)
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Convert row to formatted text
                content = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                doc = Document(
                    content=content,
                    source_file=csv_path.name,
                    document_type="csv_row",
                    section=csv_path.parent.name,
                    chunk_index=i,
                    category=category,
                    department=department,
                    confidentiality="public",
                )
                documents.append(doc)
    except Exception as e:
        print(f"Error loading CSV {csv_path}: {e}")
    return documents


def infer_department_from_path(file_path: Path) -> str:
    """Infer department from file name or path."""
    filename = file_path.name.lower()
    if "faculty" in filename or "department" in filename:
        return "General"  # Faculty files apply to all
    if "chem" in filename or "organic" in filename:
        return "Chemistry"
    if "bio" in filename:
        return "Biology"
    if "cs" in filename or "computer" in filename or "programming" in filename:
        return "Computer Science"
    if "math" in filename:
        return "Mathematics"
    return "General"


def load_text_documents(txt_path: Path) -> List[Document]:
    """Load text file and chunk it with category metadata."""
    documents = []
    category = "handbook" if "handbook" in txt_path.name else "department_info"
    department = infer_department_from_path(txt_path)
    
    try:
        content = txt_path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(content, chunk_size=500, overlap=50)
        for i, chunk in enumerate(chunks):
            doc = Document(
                content=chunk,
                source_file=txt_path.name,
                document_type="handbook" if "handbook" in txt_path.name else "info",
                section=extract_section(chunk),
                chunk_index=i,
                category=category,
                department=department,
                confidentiality="public",
            )
            documents.append(doc)
    except Exception as e:
        print(f"Error loading text {txt_path}: {e}")
    return documents


def extract_section(text: str) -> str:
    """Extract section header from chunk (first line starting with #)."""
    for line in text.split("\n"):
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Unsectioned"


def load_all_documents(data_dir: str = "./data") -> List[Document]:
    """Recursively load all documents from data directory."""
    data_path = Path(data_dir)
    all_documents = []

    # Load CSVs
    for csv_file in data_path.rglob("*.csv"):
        print(f"Loading CSV: {csv_file.relative_to(data_path)}")
        all_documents.extend(load_csv_documents(csv_file))

    # Load text files
    for txt_file in data_path.rglob("*.txt"):
        print(f"Loading text: {txt_file.relative_to(data_path)}")
        all_documents.extend(load_text_documents(txt_file))

    # TODO: Add PDF support via PyPDF2 or pdfplumber
    # for pdf_file in data_path.rglob("*.pdf"):
    #     all_documents.extend(load_pdf_documents(pdf_file))

    return all_documents


def deduplicate_documents(documents: List[Document]) -> List[Document]:
    """Remove duplicate documents by ID."""
    seen = set()
    unique = []
    for doc in documents:
        if doc.id not in seen:
            seen.add(doc.id)
            unique.append(doc)
    return unique


def embed_documents(documents: List[Document], model_name: str = "all-MiniLM-L6-v2") -> List[Document]:
    """
    Generate embeddings for documents using Sentence Transformers.
    Falls back to None if embeddings unavailable.
    """
    if not EMBEDDING_AVAILABLE:
        print("⚠ Sentence Transformers not installed. Skipping embeddings.")
        print("  Install with: pip install sentence-transformers")
        return documents

    try:
        print(f"\nLoading embedding model: {model_name}...")
        model = SentenceTransformer(model_name)
        
        print(f"Generating embeddings for {len(documents)} documents...")
        texts = [doc.content for doc in documents]
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=False)
        
        for doc, embedding in zip(documents, embeddings):
            doc.embedding = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        
        print(f"✓ Generated {len(documents)} embeddings")
        return documents
    except Exception as e:
        print(f"⚠ Error generating embeddings: {e}")
        return documents


def embed_and_store(documents: List[Document], use_embeddings: bool = True) -> None:
    """
    Embed documents and store in vector DB.
    TODO: Plug in vector store (Chroma/Pinecone) for actual storage.
    """
    if not documents:
        print("No documents to embed and store.")
        return

    print(f"\nPreparing to embed {len(documents)} documents...")
    
    # Generate embeddings if requested
    if use_embeddings:
        documents = embed_documents(documents)
    
    # Save to JSONL for testing/inspection
    output_file = "data/indexed_documents.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc.to_dict()) + "\n")
    print(f"✓ Saved {len(documents)} documents to {output_file}")

    # Preview metadata
    print("\nDocument metadata breakdown:")
    categories = {}
    for doc in documents:
        cat = doc.category or "uncategorized"
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")

    print("\nNext steps:")
    print("  1. Initialize Chroma vector DB: from_documents(documents)")
    print("  2. Build BM25 sparse index for hybrid search")
    print("  3. Test retrieval with college-specific queries")


def run_ingest(data_dir: str = "./data", use_embeddings: bool = True) -> None:
    """Main ingestion pipeline."""
    print("=" * 60)
    print("College Document Ingestion Pipeline with Embeddings")
    print("=" * 60)

    # Load
    documents = load_all_documents(data_dir)
    print(f"\n✓ Loaded {len(documents)} document chunks")

    # Deduplicate
    unique_documents = deduplicate_documents(documents)
    print(f"✓ After deduplication: {len(unique_documents)} unique documents")

    # Categorize
    doc_types = {}
    for doc in unique_documents:
        doc_types[doc.document_type] = doc_types.get(doc.document_type, 0) + 1
    print("\nDocument type breakdown:")
    for dtype, count in doc_types.items():
        print(f"  - {dtype}: {count}")

    # Embed and store
    embed_and_store(unique_documents, use_embeddings=use_embeddings)

    print("\n" + "=" * 60)
    print("Ingestion pipeline complete. Ready for retrieval wiring.")
    print("=" * 60)


if __name__ == "__main__":
    run_ingest()
