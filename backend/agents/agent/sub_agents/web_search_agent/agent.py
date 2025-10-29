# sub_agents/web_search_agent/agent.py
from google.adk.agents import Agent
from google.adk.tools import google_search
import os
from .prompts import return_web_search_agent_prompt

web_search_agent = Agent(model = os.getenv("ANALYTICS_AGENT_MODEL", "gemini-2.5-flash"),
                         name = "meruferat_web_search_agent",
                         instruction = return_web_search_agent_prompt(),
                         tools = [google_search],)
