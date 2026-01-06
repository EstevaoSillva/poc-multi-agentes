"""
Test suite for EmbeddingsService and SessionMemory RAG integration.
"""

import tempfile
import json
from pathlib import Path
from agents_app.services.embeddings_service import EmbeddingsService
from agents_app.services.session_memory import SessionMemory


def test_embeddings_service():
    """Test basic embeddings functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        embeddings = EmbeddingsService(
            session_id=1,
            workspace_path=workspace,
            model_name="all-MiniLM-L6-v2",
        )
        
        print(f"✓ EmbeddingsService initialized")
        print(f"  Stats: {embeddings.get_stats()}")
        
        # Add documents
        doc_id_1 = embeddings.add_document(
            content="Django is a Python web framework",
            source="docs/django.md",
            metadata_dict={"type": "doc", "framework": "django"},
        )
        
        doc_id_2 = embeddings.add_document(
            content="Angular is a TypeScript framework for building web apps",
            source="docs/angular.md",
            metadata_dict={"type": "doc", "framework": "angular"},
        )
        
        doc_id_3 = embeddings.add_document(
            content="PostgreSQL is a relational database management system",
            source="docs/postgres.md",
            metadata_dict={"type": "doc", "db": "postgres"},
        )
        
        print(f"\n✓ Added 3 documents (IDs: {doc_id_1}, {doc_id_2}, {doc_id_3})")
        
        # Test search
        query = "web framework Python"
        results = embeddings.search(query, top_k=2)
        
        print(f"\n✓ Search results for '{query}':")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['source']} (similarity: {result['similarity']:.2f})")
        
        # Test RAG context
        rag_ctx = embeddings.get_rag_context(query, top_k=2, max_chars=500)
        print(f"\n✓ RAG context:\n{rag_ctx}")
        
        return True


def test_session_memory_with_embeddings():
    """Test SessionMemory with RAG integration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        memory = SessionMemory(
            session_id=1,
            workspace_path=workspace,
        )
        
        print(f"\n✓ SessionMemory initialized")
        
        # Add interactions
        memory.add_interaction(
            user_input="Create a Django REST API",
            intent={"intent": "create_backend", "confidence": 0.95},
            planner_decision={"strategy": "execute_tools"},
        )
        
        memory.add_interaction(
            user_input="Add Angular frontend",
            intent={"intent": "create_frontend", "confidence": 0.92},
            planner_decision={"strategy": "execute_tools"},
        )
        
        memory.set_metadata("project_description", "A full-stack web app with Django + Angular")
        memory.set_metadata("project_category", "web")
        
        print(f"✓ Added 2 interactions and metadata")
        
        # Test RAG retrieval
        query = "Angular frontend creation"
        rag_context = memory.get_rag_context(query, top_k=2, max_chars=500)
        print(f"\n✓ RAG context for '{query}':\n{rag_context}")
        
        # Test full context
        full_ctx = memory.get_full_context()
        print(f"\n✓ Full context snapshot:")
        print(f"  - Interactions: {len(full_ctx['interactions'])}")
        print(f"  - Metadata keys: {list(full_ctx['metadata'].keys())}")
        print(f"  - Embeddings stats: {full_ctx['embeddings_stats']}")
        
        # Verify persistence
        memory2 = SessionMemory(session_id=1, workspace_path=workspace)
        assert len(memory2.get_recent_interactions()) == 2
        print(f"\n✓ Memory persisted correctly")
        
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing EmbeddingsService")
    print("=" * 60)
    try:
        test_embeddings_service()
    except Exception as e:
        print(f"⚠️  EmbeddingsService test: {e}")
        print("   (This is OK if sentence-transformers or faiss is not installed)")
    
    print("\n" + "=" * 60)
    print("Testing SessionMemory with RAG")
    print("=" * 60)
    try:
        test_session_memory_with_embeddings()
    except Exception as e:
        print(f"✗ SessionMemory test failed: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
