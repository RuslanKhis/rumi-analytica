from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import ToolContext
import sys
from .sub_agents.web_search_agent.agent import web_search_agent

async def call_web_search_agent(question: str, tool_context: ToolContext) -> str:
    """ Calls the web search agent Meruferat to answer the questions requiring internet access for current events or general knowledge. 
    
    Args: question: The user's question for the web search agent.
          tool_context: Shared context for state management.
    """
    try: 
        agent_tool = AgentTool(agent=web_search_agent)
        output = await agent_tool.run_async(
            args={"request": question},
            tool_context=tool_context
        )
        if output is None: 
            return "No response from Meruferat web search agent."
        return str(output)
    except Exception as e: 
        error_msg = f"Error calling Meruferat web search agent: {str(e)}"
        print(f"[ERROR] {error_msg}", file=sys.stderr)
        return error_msg