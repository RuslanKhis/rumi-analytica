# data_science/sub_agents/ga4_template/agent.py
import os
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.bigquery import BigQueryToolset

from . import tools
from .prompts import return_instructions_ga4_template

# Instantiate the BigQuery toolset here
bigquery_toolset = BigQueryToolset(tool_filter=["execute_sql"])

# Define the GA4 Template Agent
ga4_template_agent = Agent(
    model=os.getenv("GA4_AGENT_MODEL", "gemini-1.5-flash"),
    name="ga4_template_agent",
    instruction=return_instructions_ga4_template(),
    tools=[
        tools.build_ga4_query_from_template,
        bigquery_toolset,
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)