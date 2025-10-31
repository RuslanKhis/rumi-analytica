# data_science/sub_agents/ga4_template/tools.py

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from google.adk.tools import ToolContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from .query_template_library import QUERY_TEMPLATE_LIBRARY

# This part remains the same
bigquery_toolset = BigQueryToolset(
    tool_filter=["execute_sql"],
    bigquery_tool_config=BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        max_query_result_rows=100,
    )
)
execute_sql_tool = bigquery_toolset.get_tool("execute_sql")

def _get_default_dates():
    """Returns default start and end dates (YYYYMMDD)."""
    today = datetime.now(timezone.utc).date()
    end_date = today - timedelta(days=1)
    start_date = today - timedelta(days=8)
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")



def execute_ga4_template_query(template_name: str, parameters: Dict[str, Any], tool_context: ToolContext) -> Dict:
    """Executes a predefined GA4 BigQuery template to answer a user's question about Google Analytics data.

    Args:
        template_name: The name of the template to execute. Must be one of the available template names.
        parameters: A dictionary of parameters for the template, such as 'start_date', 'end_date', 'event_name', etc. Dates should be in YYYYMMDD format.
    """
    # 1. Validate Template
    if not template_name or template_name not in QUERY_TEMPLATE_LIBRARY:
        return {"status": "ERROR", "message": f"Invalid template '{template_name}'. Please choose from the available templates."}

    # 2. Get Environment Config
    project_id = os.getenv("BQ_COMPUTE_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT"))
    dataset_id = os.getenv("BQ_DATASET_ID")
    if not project_id or not dataset_id:
        return {"status": "ERROR", "message": "Missing BQ_COMPUTE_PROJECT_ID or BQ_DATASET_ID environment variables."}

    # 3. Prepare SQL Parameters
    sql_template = QUERY_TEMPLATE_LIBRARY[template_name]["template"]
    start_def, end_def = _get_default_dates()
    
    final_params = {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "start_date": parameters.get("start_date", start_def),
        "end_date": parameters.get("end_date", end_def),
    }
    for param_key in ["event_name", "country_name", "property_key", "campaign_name"]:
        if param_key in parameters:
            final_params[param_key] = parameters[param_key]

    # 4. Format the SQL Query
    try:
        final_sql = sql_template.format(**final_params)
    except KeyError as e:
        return {"status": "ERROR", "message": f"Template '{template_name}' is missing a required parameter: {e}"}

    # 5. Execute the Query using the ADK's built-in tool
    print(f"Executing GA4 Template Query:\n{final_sql}")
    execution_result = execute_sql_tool.call(
        sql=final_sql,
        project_id=project_id,
        tool_context=tool_context
    )

    # 6. Store details in context and return result
    tool_context.state["ga4_query_details"] = {
        "chosen_template": template_name,
        "extracted_parameters": parameters,
        "final_sql": final_sql,
        "execution_result": execution_result
    }
    
    return execution_result