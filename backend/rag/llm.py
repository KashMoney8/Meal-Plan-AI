from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import Settings

_settings = Settings()

def get_llm():
    return ChatVertexAI(
        model=_settings.VERTEX_MODEL,           # e.g., "gemini-1.5-pro"
        location=_settings.VERTEX_LOCATION,     # e.g., "us-central1"
        project=_settings.GOOGLE_CLOUD_PROJECT,
        temperature=0.3,
        max_output_tokens=1024,
    )

def simple_completion(system_prompt: str, user_prompt: str) -> str:
    llm = get_llm()
    resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    return resp.content
