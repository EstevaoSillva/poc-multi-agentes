"""
Stream service - wraps orchestrator to provide streaming responses.

Allows agents to emit progress updates in real-time via WebSocket.
"""

import json
import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime


class StreamMessage:
    """Message sent via stream."""

    def __init__(
        self,
        event_type: str,
        data: Dict[str, Any],
        timestamp: Optional[str] = None,
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_json(self) -> str:
        """Convert to JSON for WebSocket transmission."""
        return json.dumps({
            "event": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
        }, ensure_ascii=False)

    @staticmethod
    def from_json(payload: str) -> "StreamMessage":
        """Parse from JSON."""
        obj = json.loads(payload)
        return StreamMessage(
            event_type=obj["event"],
            data=obj["data"],
            timestamp=obj.get("timestamp"),
        )


class StreamEventType:
    """Standard stream event types."""
    # Session & context
    SESSION_STARTED = "session_started"
    CONTEXT_LOADED = "context_loaded"
    
    # Intent & planning
    INTENT_DETECTED = "intent_detected"
    PLAN_CREATED = "plan_created"
    
    # RAG & retrieval
    RAG_RETRIEVING = "rag_retrieving"
    RAG_RETRIEVED = "rag_retrieved"
    
    # Tool execution
    TOOL_EXECUTING = "tool_executing"
    TOOL_EXECUTED = "tool_executed"
    
    # Agent execution
    AGENT_THINKING = "agent_thinking"
    AGENT_GENERATED = "agent_generated"
    
    # Final result
    RESPONSE_COMPLETE = "response_complete"
    ERROR_OCCURRED = "error_occurred"
    
    # Connection
    HEARTBEAT = "heartbeat"


class StreamService:
    """
    Service to stream orchestrator execution in real-time.

    Provides:
    - Callback hooks for agent lifecycle events
    - Message streaming to WebSocket consumers
    - Progress tracking and ETA estimation
    """

    def __init__(self, session_id: int, send_callback: Callable):
        """
        Initialize streaming service.

        Args:
            session_id: Session ID
            send_callback: Async function(message: str) to send to WebSocket
        """
        self.session_id = session_id
        self.send_callback = send_callback
        self.event_count = 0
        self.start_time = datetime.utcnow()
        self.is_connected = True

    async def emit(self, event_type: str, data: Optional[Dict] = None) -> None:
        """
        Emit a stream event.

        Args:
            event_type: Type of event (use StreamEventType constants)
            data: Event-specific data
        """
        if not self.is_connected:
            return

        self.event_count += 1
        message = StreamMessage(
            event_type=event_type,
            data=data or {},
        )

        try:
            await self.send_callback(message.to_json())
        except Exception as e:
            print(f"Error sending message: {e}")
            self.is_connected = False

    async def emit_intent_detected(self, intent: str, confidence: float) -> None:
        """Emit intent detection event."""
        await self.emit(
            StreamEventType.INTENT_DETECTED,
            {
                "intent": intent,
                "confidence": confidence,
            },
        )

    async def emit_plan_created(self, plan: Dict) -> None:
        """Emit plan creation event."""
        await self.emit(
            StreamEventType.PLAN_CREATED,
            {
                "strategy": plan.get("strategy"),
                "tools": plan.get("tools", []),
                "description": plan.get("description"),
            },
        )

    async def emit_rag_retrieving(self, query: str) -> None:
        """Emit RAG retrieval start."""
        await self.emit(
            StreamEventType.RAG_RETRIEVING,
            {"query": query},
        )

    async def emit_rag_retrieved(self, results: list, count: int) -> None:
        """Emit RAG retrieval complete."""
        await self.emit(
            StreamEventType.RAG_RETRIEVED,
            {
                "count": count,
                "sources": [r.get("source") for r in results[:5]],
            },
        )

    async def emit_tool_executing(self, tool_name: str, args: Dict) -> None:
        """Emit tool execution start."""
        await self.emit(
            StreamEventType.TOOL_EXECUTING,
            {
                "tool": tool_name,
                "args_keys": list(args.keys()),
            },
        )

    async def emit_tool_executed(self, tool_name: str, status: str) -> None:
        """Emit tool execution complete."""
        await self.emit(
            StreamEventType.TOOL_EXECUTED,
            {
                "tool": tool_name,
                "status": status,
            },
        )

    async def emit_agent_thinking(self, agent_name: str, task: str) -> None:
        """Emit agent thinking start."""
        await self.emit(
            StreamEventType.AGENT_THINKING,
            {
                "agent": agent_name,
                "task": task,
            },
        )

    async def emit_agent_generated(self, agent_name: str, content_length: int) -> None:
        """Emit agent generation complete."""
        await self.emit(
            StreamEventType.AGENT_GENERATED,
            {
                "agent": agent_name,
                "length": content_length,
            },
        )

    async def emit_response_complete(self, result: Dict) -> None:
        """Emit final response complete event."""
        await self.emit(
            StreamEventType.RESPONSE_COMPLETE,
            {
                "status": "success",
                "event_count": self.event_count,
                "duration_ms": (datetime.utcnow() - self.start_time).total_seconds() * 1000,
            },
        )

    async def emit_error(self, error_message: str, error_type: str = "unknown") -> None:
        """Emit error event."""
        await self.emit(
            StreamEventType.ERROR_OCCURRED,
            {
                "error": error_message,
                "type": error_type,
            },
        )

    async def heartbeat(self) -> None:
        """Send heartbeat to keep connection alive."""
        await self.emit(StreamEventType.HEARTBEAT, {"session_id": self.session_id})


class StreamingOrchestratorWrapper:
    """
    Wraps orchestrator calls to inject streaming callbacks.

    Usage:
        wrapper = StreamingOrchestratorWrapper(orchestrator, stream_service)
        result = await wrapper.run_with_streaming(session_id, user_input)
    """

    def __init__(self, orchestrator, stream_service: StreamService):
        """
        Args:
            orchestrator: CopilotOrchestrator instance
            stream_service: StreamService instance
        """
        self.orchestrator = orchestrator
        self.stream = stream_service

    async def run_with_streaming(
        self,
        session_id: int,
        user_input: str,
        use_teams: Optional[bool] = None,
    ) -> Dict:
        """
        Execute orchestrator with streaming updates.

        Emits real-time events as execution progresses.

        Args:
            session_id: Session ID
            user_input: User request
            use_teams: Force team mode

        Returns:
            Orchestrator result dict
        """
        try:
            # Emit session start
            await self.stream.emit(
                StreamEventType.SESSION_STARTED,
                {
                    "session_id": session_id,
                    "user_input": user_input[:100],  # First 100 chars
                },
            )

            # Run orchestrator (sync call wrapped in async)
            # Note: In production, you'd want true async agents
            result = self.orchestrator.run(session_id, user_input, use_teams)

            # Emit final result
            await self.stream.emit_response_complete(result)

            return result

        except Exception as e:
            await self.stream.emit_error(str(e), "orchestrator_error")
            raise

    async def streaming_generator(self, text: str, chunk_size: int = 50):
        """
        Helper: stream text in chunks (for generated code, etc).

        Usage:
            async for chunk in wrapper.streaming_generator(code):
                await stream_service.emit('text_chunk', {'chunk': chunk})
        """
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
            # Simulate small delay to avoid overwhelming client
            await asyncio.sleep(0.01)
