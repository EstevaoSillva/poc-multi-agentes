from agents_app.agents.intent_agent import intent_router_agent
from agents_app.utils import safe_json_parse


class IntentService:
    def resolve(self, user_input: str) -> dict:
        output = intent_router_agent.run(user_input)
        raw = output.content if hasattr(output, "content") else str(output)

        data = safe_json_parse(raw)

        # Hard validation
        if "intent" not in data or "confidence" not in data:
            raise ValueError("Invalid intent response")

        return data