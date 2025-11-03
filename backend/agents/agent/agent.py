import os
from google.adk.agents import Agent
from .prompts import return_root_agent_prompt
from .tools import call_web_search_agent, call_db_agent, call_data_science_agent, call_document_agent, call_econometrics_agent, call_ga4_template_agent
from google.genai import types
from google.adk.tools import load_artifacts

root_agent = Agent(
    # The 'name' parameter inside the Agent should match your folder name
    # for consistency, though 'root_agent' is the critical variable name.
    name="rumi_analytica",

    # Use an environment variable for the model, with a sensible default.
    model=os.getenv("ANALYTICS_AGENT_MODEL", "gemini-2.5-pro"),

    # Keep complex instructions in a separate file or function for cleanliness.
    instruction=return_root_agent_prompt(),
    global_instruction=f"You are Rumi and analytics agent that helps users analyze data and generate insights and act upon them",
    description="An agent for performing data analysis by writing and executing Python code.", 
    tools=[call_web_search_agent, load_artifacts, call_db_agent, call_data_science_agent, call_document_agent, call_econometrics_agent, call_ga4_template_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)