"""
Session memory management - stores and retrieves interaction history and context.
Provides efficient context building for RAG-enabled agent pipeline.
"""

from datetime import datetime
from typing import Optional
from pathlib import Path
import json

from django.conf import settings

from agents_app.api.models import Interaction
from agents_app.services.embeddings_service import EmbeddingsService
from agents_app.services.knowledge_ingestion_service import KnowledgeIngestionService


class SessionMemory:
    """
    Manages session context and interaction history.
    
    Stores:
    - Last N interactions (messages, intents, planner decisions, responses)
    - Session metadata (description, category, stack recommendations)
    - Vector embeddings metadata (for RAG integration)
    - Open problems and context clues
    """

    def __init__(self, session_id: int, workspace_path: Path, max_history: int = 10):
        self.session_id = session_id
        self.workspace_path = workspace_path
        self.max_history = max_history
        self._memory_file = workspace_path / "memory.json"
        
        # Initialize embeddings service for RAG
        self.embeddings = EmbeddingsService(session_id, workspace_path)
        self.knowledge_service = KnowledgeIngestionService(
            session_id=session_id,
            workspace_path=workspace_path,
            embeddings_service=self.embeddings,
            source_paths=getattr(settings, "KNOWLEDGE_SOURCES", []),
        )
        
        self._load_from_disk()
        if getattr(settings, "KNOWLEDGE_AUTO_INDEX", False):
            try:
                self.knowledge_service.reindex(force=False)
            except Exception:
                pass

    def _load_from_disk(self) -> dict:
        """Load memory from workspace disk if exists."""
        if self._memory_file.exists():
            try:
                with open(self._memory_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                    return self._data
            except (json.JSONDecodeError, IOError):
                pass
        
        # Initialize empty structure
        self._data = {
            "session_id": self.session_id,
            "created_at": datetime.utcnow().isoformat(),
            "interactions": [],
            "metadata": {},
            "embeddings_index": {},
        }
        return self._data

    def _save_to_disk(self):
        """Persist memory to disk."""
        self._memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._memory_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def add_interaction(
        self,
        user_input: str,
        intent: Optional[dict] = None,
        planner_decision: Optional[dict] = None,
        response: Optional[dict] = None,
        tool_calls: Optional[list] = None,
    ) -> dict:
        """
        Record an interaction in memory.
        
        Args:
            user_input: The user's message
            intent: Intent router output (intent, confidence, reason)
            planner_decision: Planner agent output (structure, next_steps)
            response: Final response from orchestrator
            tool_calls: Tools executed during this interaction
        
        Returns:
            Interaction record
        """
        interaction = {
            "id": len(self._data["interactions"]),
            "timestamp": datetime.utcnow().isoformat(),
            "user_input": user_input,
            "intent": intent or {},
            "planner_decision": planner_decision or {},
            "response": response or {},
            "tool_calls": tool_calls or [],
        }
        
        self._data["interactions"].append(interaction)
        
        # Embed user input for RAG
        self.embeddings.add_document(
            content=user_input,
            source=f"interaction_{len(self._data['interactions'])-1}",
            metadata_dict={"type": "user_input", "intent": intent.get("intent") if intent else None},
        )
        
        # Keep only last N interactions in memory
        if len(self._data["interactions"]) > self.max_history:
            self._data["interactions"] = self._data["interactions"][-self.max_history:]
        
        self._save_to_disk()
        return interaction

    def get_recent_interactions(self, limit: Optional[int] = None) -> list:
        """Get recent interactions (default: last 5)."""
        limit = limit or 5
        return self._data["interactions"][-limit:]

    def get_interaction_context(self, max_chars: int = 2000) -> str:
        """
        Build a string context from recent interactions for agent prompts.
        Truncates to max_chars to fit in token budget.
        """
        recent = self.get_recent_interactions(limit=5)
        
        lines = []
        for inter in recent:
            user = inter.get("user_input", "")[:100]
            intent = inter.get("intent", {}).get("intent", "unknown")
            lines.append(f"- User: {user} | Intent: {intent}")
        
        context = "Recent interactions:\n" + "\n".join(lines)
        return context[:max_chars]

    def set_metadata(self, key: str, value) -> None:
        """Store session metadata (project description, category, etc)."""
        self._data["metadata"][key] = value
        self._save_to_disk()

    def get_metadata(self, key: str, default=None):
        """Retrieve session metadata."""
        return self._data["metadata"].get(key, default)

    def add_embedding_reference(self, file_path: str, embedding_id: str, metadata: dict = None) -> None:
        """
        Register a file/snippet that was embedded (for RAG).
        
        Args:
            file_path: Path to the file (e.g., "backend/models.py")
            embedding_id: ID in the vector DB
            metadata: Extra metadata (content hash, line range, etc)
        """
        if file_path not in self._data["embeddings_index"]:
            self._data["embeddings_index"][file_path] = []
        
        self._data["embeddings_index"][file_path].append({
            "embedding_id": embedding_id,
            "metadata": metadata or {},
            "indexed_at": datetime.utcnow().isoformat(),
        })
        
        self._save_to_disk()

    def get_embedding_references(self, file_path: Optional[str] = None) -> dict:
        """Get embedding index (all or for a specific file)."""
        if file_path:
            return self._data["embeddings_index"].get(file_path, [])
        return self._data["embeddings_index"]

    def get_full_context(self) -> dict:
        """
        Return full context snapshot for agents.
        Includes recent interactions, metadata, and embeddings index.
        """
        return {
            "interactions": self.get_recent_interactions(),
            "context_string": self.get_interaction_context(),
            "metadata": self._data["metadata"],
            "embeddings_index": self._data["embeddings_index"],
            "embeddings_stats": self.embeddings.get_stats(),
            "knowledge_stats": self.knowledge_service.stats(),
            "session_id": self.session_id,
        }

    def get_rag_context(self, query: str, top_k: int = 3, max_chars: int = 1000) -> str:
        """
        Retrieve RAG context from embeddings for a query.
        
        Args:
            query: User query or prompt
            top_k: Number of similar documents to retrieve
            max_chars: Max characters in returned context
        
        Returns:
            Formatted RAG context string for agent prompts
        """
        return self.embeddings.get_rag_context(query, top_k=top_k, max_chars=max_chars)

    def clear_interactions(self) -> None:
        """Clear interaction history but keep metadata."""
        self._data["interactions"] = []
        self._save_to_disk()

    def to_dict(self) -> dict:
        """Export full memory as dict."""
        return self._data

    def reindex_knowledge(self, force: bool = False) -> dict:
        return self.knowledge_service.reindex(force=force)

    def get_knowledge_stats(self) -> dict:
        return self.knowledge_service.stats()
