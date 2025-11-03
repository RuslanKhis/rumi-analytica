# data_science/sub_agents/ga4_bigquery_agent/tools.py

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from .query_template_library import QUERY_TEMPLATE_LIBRARY

def _get_default_dates():
    """Returns default start and end dates (YYYYMMDD)."""
    today = datetime.now(timezone.utc).date()
    end_date = today - timedelta(days=1)
    start_date = today - timedelta(days=8)
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")

def build_ga4_query_from_template(template_name: str, parameters: Dict[str, Any]) -> str:
    """
    Selects a GA4 BigQuery template and formats it with the provided parameters to create a complete SQL query.

    Args:
        template_name: The name of the template to use.
        parameters: A dictionary of parameters for the template, such as 'start_date', 'end_date', etc.
    
    Returns:
        A JSON string containing the final SQL query or an error message.
    """
    if not template_name or template_name not in QUERY_TEMPLATE_LIBRARY:
        return json.dumps({"status": "ERROR", "message": f"Invalid template '{template_name}'. Please choose from the available templates."})

    project_id = os.getenv("BQ_COMPUTE_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT"))
    dataset_id = os.getenv("BQ_DATASET_ID")
    if not project_id or not dataset_id:
        return json.dumps({"status": "ERROR", "message": "Missing BQ_COMPUTE_PROJECT_ID or BQ_DATASET_ID environment variables."})

    sql_template = QUERY_TEMPLATE_LIBRARY[template_name]["template"]
    start_def, end_def = _get_default_dates()
    
    final_params = {
        "project_id": project_id,
        "dataset_id": dataset_id,
        "start_date": parameters.get("start_date", start_def),
        "end_date": parameters.get("end_date", end_def),
    }
    # Add any other parameters from the user input
    for param_key in ["event_name", "country_name", "property_key", "campaign_name"]:
        if param_key in parameters:
            final_params[param_key] = parameters[param_key]

    try:
        final_sql = sql_template.format(**final_params)
        print(f"Built GA4 Query:\n{final_sql}")
        # Return the SQL in a structured JSON format for the agent to parse
        return json.dumps({"status": "SUCCESS", "sql": final_sql})
    except KeyError as e:
        return json.dumps({"status": "ERROR", "message": f"Template '{template_name}' is missing a required parameter: {e}"})