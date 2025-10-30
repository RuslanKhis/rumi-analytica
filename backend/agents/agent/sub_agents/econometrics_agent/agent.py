from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor
import os
from .prompts import return_econometrics_agent_prompt

econometrics_agent = Agent(
    name="econometrics_agent",
    model=os.getenv("ECONOMETRICS_AGENT_MODEL", "gemini-2.5-flash"),
    instruction=return_econometrics_agent_prompt(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ))