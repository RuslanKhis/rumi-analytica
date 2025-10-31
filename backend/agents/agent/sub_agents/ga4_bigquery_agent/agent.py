# data_science/sub_agents/ga4_template/agent.py
import os
from google.adk.agents import Agent
from google.genai import types

from . import tools
from .prompts import return_instructions_ga4_template

# Define the GA4 Template Agent
ga4_template_agent = Agent(
    # Use a powerful model that is good with complex function calling
    model=os.getenv("GA4_AGENT_MODEL", "gemini-1.5-pro-latest"),
    name="ga4_template_agent",
    instruction=return_instructions_ga4_template(),
    tools=[
        tools.execute_ga4_template_query,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)