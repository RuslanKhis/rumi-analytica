import os
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from .prompts import return_document_agent_prompt

DATA_STORE_PATH = "projects/rumi-analytica/locations/global/collections/default_collection/dataStores/rumi-analytica-books_1761800267595"

vertexai_search_tool = VertexAiSearchTool(
    data_store_id=DATA_STORE_PATH
)

document_agent = Agent(
    name="document_agent",
    model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"),
    instruction=return_document_agent_prompt(),
    tools=[vertexai_search_tool],
    description="An agent that searches through 3 chapters of book about Digital Marketing to answer user questions.",
)