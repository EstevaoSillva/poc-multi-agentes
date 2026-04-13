"""
WebSocket client for testing streaming API.

Usage:
    python test_streaming_client.py
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime


class StreamingClient:
    """WebSocket client for streaming orchestrator execution."""

    def __init__(self, uri: str = "ws://localhost:8000/ws/stream/1/"):
        self.uri = uri
        self.websocket = None
        self.event_count = 0

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"✓ Connected to {self.uri}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False

    async def send_run(self, session_id: int, user_input: str):
        """Send run request."""
        payload = {
            "action": "run",
            "session_id": session_id,
            "user_input": user_input,
        }
        await self.websocket.send(json.dumps(payload))
        print(f"→ Sent: {payload}")

    async def receive_events(self):
        """Listen for events from server."""
        try:
            while True:
                message = await self.websocket.recv()
                self.event_count += 1

                try:
                    event = json.loads(message)
                    await self.handle_event(event)
                except json.JSONDecodeError:
                    print(f"? Received invalid JSON: {message}")

        except websockets.exceptions.ConnectionClosed:
            print("✗ Connection closed by server")
        except Exception as e:
            print(f"✗ Error receiving: {e}")

    async def handle_event(self, event: dict):
        """Handle received event."""
        event_type = event.get("event")
        data = event.get("data", {})
        timestamp = event.get("timestamp", "")

        # Emoji based on event type
        emoji_map = {
            "session_started": "🚀",
            "intent_detected": "🎯",
            "plan_created": "📋",
            "rag_retrieving": "🔍",
            "rag_retrieved": "📚",
            "tool_executing": "⚙️",
            "tool_executed": "✓",
            "agent_thinking": "💭",
            "agent_generated": "📝",
            "response_complete": "✅",
            "error_occurred": "❌",
            "heartbeat": "💓",
            "execution_result": "🎬",
        }

        emoji = emoji_map.get(event_type, "•")

        print(f"\n{emoji} [{event_type}]")
        if data:
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"    {key}: {json.dumps(value, indent=6)}")
                else:
                    print(f"    {key}: {value}")

    async def send_heartbeat(self):
        """Send heartbeat."""
        await self.websocket.send(json.dumps({"action": "heartbeat"}))

    async def close(self):
        """Close connection."""
        if self.websocket:
            await self.websocket.close()
            print("✓ Connection closed")

    async def run(self, session_id: int = 1, user_input: str = "Create a Django REST API"):
        """Run test scenario."""
        if not await self.connect():
            return

        try:
            # Send run request
            await self.send_run(session_id, user_input)

            # Listen for events
            receive_task = asyncio.create_task(self.receive_events())

            # Send heartbeat every 30 seconds
            while True:
                try:
                    await asyncio.sleep(30)
                    await self.send_heartbeat()
                except asyncio.CancelledError:
                    break

        except KeyboardInterrupt:
            print("\n⛔ Interrupted by user")
        finally:
            await self.close()


async def main():
    """Main test function."""
    print("=" * 60)
    print("WebSocket Streaming Client")
    print("=" * 60)

    # Parse arguments
    session_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    user_input = sys.argv[2] if len(sys.argv) > 2 else "Create a REST API backend"
    uri = sys.argv[3] if len(sys.argv) > 3 else "ws://localhost:8000/ws/stream/1/"

    client = StreamingClient(uri)
    await client.run(session_id=session_id, user_input=user_input)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
