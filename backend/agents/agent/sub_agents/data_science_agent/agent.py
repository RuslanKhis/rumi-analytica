from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor
import os
from .prompts import return_data_science_agent_prompt

data_science_agent = Agent(
    name="data_science_agent",
    model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"),
    instruction=return_data_science_agent_prompt(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ))