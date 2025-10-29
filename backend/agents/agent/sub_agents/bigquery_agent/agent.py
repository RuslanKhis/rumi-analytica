# data_science/sub_agents/bigquery/agent.py
import os
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types

from . import tools
from .prompts import return_instructions_bigquery

ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"

def setup_before_agent_call(callback_context: CallbackContext) -> None:
    """Setup the agent."""
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = \
            tools.get_database_settings()

def store_results_in_context(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Store the successful query results in the shared context for other agents."""
    if tool.name == ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL and tool_response.get("status") == "SUCCESS":
        tool_context.state["query_result"] = tool_response.get("rows")
    return None

# The ADK's BigQueryToolset will use Application Default Credentials automatically
bigquery_toolset = BigQueryToolset(
    tool_filter=[ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL],
    bigquery_tool_config=BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        max_query_result_rows=100,
        # Don't pass credentials - let it use default
    )
)

# Define the Database Agent
database_agent = Agent(
    model=os.getenv("BIGQUERY_AGENT_MODEL", "gemini-2.5-flash"),
    name="database_agent",
    instruction=return_instructions_bigquery(),
    tools=[
        tools.initial_bq_nl2sql,
        bigquery_toolset,
    ],
    after_tool_callback=store_results_in_context,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)