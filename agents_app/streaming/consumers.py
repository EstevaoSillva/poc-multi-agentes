"""
WebSocket consumer for streaming agent execution.

Handles:
- Client connection/disconnection
- Message reception
- Streaming response delivery
- Error handling and heartbeat
"""

import json
import asyncio
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

from agents_app.orchestrator import CopilotOrchestrator
from agents_app.streaming.stream_service import (
    StreamService,
    StreamingOrchestratorWrapper,
    StreamEventType,
)


class StreamingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming orchestrator execution.

    Message format (JSON):
    {
        "action": "run" | "heartbeat" | "cancel",
        "session_id": <int>,
        "user_input": "<string>"
    }

    Events sent to client:
    {
        "event": "<event_type>",
        "data": {...},
        "timestamp": "<iso-datetime>"
    }
    """

    async def connect(self):
        """Accept WebSocket connection."""
        self.session_id = self.scope.get("url_route", {}).get("kwargs", {}).get("session_id")
        self.stream_service = None
        self.orchestrator = None
        self.heartbeat_task = None

        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Handle disconnection."""
        # Cancel heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        print(f"WebSocket disconnected: {self.channel_name} (code: {close_code})")

    async def receive(self, text_data):
        """
        Receive message from WebSocket client.

        Expects JSON with action + params.
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
            return

        action = data.get("action")

        if action == "run":
            await self.handle_run(data)
        elif action == "heartbeat":
            await self.send_heartbeat()
        elif action == "cancel":
            await self.handle_cancel()
        else:
            await self.send_error(f"Unknown action: {action}")

    async def handle_run(self, data: dict):
        """
        Handle 'run' action - execute orchestrator with streaming.

        Args:
            data: {"session_id": int, "user_input": str}
        """
        payload_session_id = data.get("session_id")
        session_id = payload_session_id or self.session_id
        user_input = data.get("user_input")

        if not session_id or not user_input:
            await self.send_error("Missing session_id or user_input")
            return
        if payload_session_id and self.session_id and int(payload_session_id) != int(self.session_id):
            await self.send_error("session_id in payload does not match route session_id")
            return

        self.session_id = session_id

        try:
            # Create stream service (sends to this consumer)
            self.stream_service = StreamService(
                session_id=session_id,
                send_callback=self.send_json_async,
            )

            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

            # Initialize orchestrator from workspace
            workspace_path = settings.WORKSPACE_PATH
            self.orchestrator = CopilotOrchestrator(workspace_path)

            # Create streaming wrapper
            wrapper = StreamingOrchestratorWrapper(
                self.orchestrator,
                self.stream_service,
            )

            # Run with streaming
            result = await wrapper.run_with_streaming(
                session_id,
                user_input,
            )

            # Send final result
            await self.send_event("execution_result", result)

        except Exception as e:
            await self.send_error(str(e), "execution_error")

    async def handle_cancel(self):
        """Handle cancel request."""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        await self.send_event(StreamEventType.HEARTBEAT, {"status": "cancelled"})

    async def send_event(self, event_type: str, data: dict):
        """Send event to client."""
        message = {
            "event": event_type,
            "data": data,
            "timestamp": self.get_timestamp(),
        }
        await self.send_json(message)

    async def send_json_async(self, json_str: str):
        """Send raw JSON string (callback for StreamService)."""
        try:
            await self.send(text_data=json_str)
        except Exception as e:
            print(f"Error sending JSON: {e}")

    async def send_error(self, message: str, error_type: str = "error"):
        """Send error event."""
        await self.send_event(StreamEventType.ERROR_OCCURRED, {
            "error": message,
            "type": error_type,
        })

    async def send_heartbeat(self):
        """Send heartbeat event."""
        await self.send_event(StreamEventType.HEARTBEAT, {
            "session_id": self.session_id,
            "connected": True,
        })

    async def heartbeat_loop(self):
        """Periodic heartbeat to keep connection alive."""
        try:
            while True:
                await asyncio.sleep(30)  # 30 second heartbeat
                await self.send_heartbeat()
        except asyncio.CancelledError:
            pass

    @staticmethod
    def get_timestamp() -> str:
        """Get ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
