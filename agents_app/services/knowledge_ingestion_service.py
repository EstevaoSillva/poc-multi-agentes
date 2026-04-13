import hashlib
import json
from pathlib import Path
from typing import Dict, List


class KnowledgeIngestionService:
    def __init__(
        self,
        session_id: int,
        workspace_path: Path,
        embeddings_service,
        source_paths: List[str],
        max_chunk_chars: int = 1200,
        chunk_overlap: int = 200,
    ):
        self.session_id = session_id
        self.workspace_path = workspace_path
        self.embeddings = embeddings_service
        self.max_chunk_chars = max_chunk_chars
        self.chunk_overlap = chunk_overlap
        self.source_paths = [Path(p).expanduser().resolve() for p in source_paths if p]

        vectors_dir = workspace_path / "vectors"
        vectors_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = vectors_dir / "knowledge_state.json"
        self._state = self._load_state()

    def _load_state(self) -> Dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {
            "session_id": self.session_id,
            "indexed_chunks": {},
            "last_run": None,
        }

    def _save_state(self):
        self.state_path.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _discover_files(self) -> List[Path]:
        files = []
        for source_root in self.source_paths:
            if not source_root.exists():
                continue
            for path in source_root.rglob("*.md"):
                if path.is_file():
                    files.append(path)
        return sorted(files)

    def _split_chunks(self, content: str) -> List[str]:
        text = (content or "").strip()
        if not text:
            return []

        if len(text) <= self.max_chunk_chars:
            return [text]

        chunks = []
        step = max(1, self.max_chunk_chars - self.chunk_overlap)
        for start in range(0, len(text), step):
            chunk = text[start:start + self.max_chunk_chars].strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    @staticmethod
    def _hash_text(content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def reindex(self, force: bool = False) -> Dict:
        files = self._discover_files()
        indexed = 0
        skipped = 0
        errors = []

        if force:
            self._state["indexed_chunks"] = {}

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                chunks = self._split_chunks(content)
                rel_source = str(file_path)

                for idx, chunk in enumerate(chunks):
                    chunk_source = f"knowledge::{rel_source}#chunk_{idx}"
                    chunk_hash = self._hash_text(chunk)

                    if self._state["indexed_chunks"].get(chunk_source) == chunk_hash:
                        skipped += 1
                        continue

                    doc_id = self.embeddings.add_document(
                        content=chunk,
                        source=chunk_source,
                        metadata_dict={
                            "type": "knowledge",
                            "file_path": rel_source,
                            "chunk_index": idx,
                        },
                    )
                    if doc_id is None:
                        skipped += 1
                        continue

                    self._state["indexed_chunks"][chunk_source] = chunk_hash
                    indexed += 1

            except Exception as exc:
                errors.append({"file": str(file_path), "error": str(exc)})

        from datetime import datetime
        self._state["last_run"] = datetime.utcnow().isoformat()
        self._save_state()

        return {
            "session_id": self.session_id,
            "knowledge_sources": [str(p) for p in self.source_paths],
            "files_scanned": len(files),
            "chunks_indexed": indexed,
            "chunks_skipped": skipped,
            "errors": errors,
            "state_file": str(self.state_path),
        }

    def stats(self) -> Dict:
        return {
            "session_id": self.session_id,
            "knowledge_sources": [str(p) for p in self.source_paths],
            "known_chunks": len(self._state.get("indexed_chunks", {})),
            "last_run": self._state.get("last_run"),
            "state_file": str(self.state_path),
        }

