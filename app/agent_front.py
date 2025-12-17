import os
from agno.models.groq import Groq

frotend_model = Groq(
    id="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_FRONTEND_KEY")
)
