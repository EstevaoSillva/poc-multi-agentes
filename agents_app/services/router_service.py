from agents_app.agents.router_agent import router_agent


class RouterService:
    def route(self, user_input: str) -> str:
        result = router_agent.run(user_input)
        return result.strip()