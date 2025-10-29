import datetime
import os
import sys
import traceback
import numpy as np
import pandas as pd
from ...utils.utils import get_env_var
from google.adk.tools import ToolContext
from google.adk.tools.bigquery.client import get_bigquery_client
from google.cloud import bigquery
from google.genai import Client

dataset_id = get_env_var("BQ_DATASET_ID")
data_project = get_env_var("BQ_DATA_PROJECT_ID")
compute_project = get_env_var("BQ_COMPUTE_PROJECT_ID")
vertex_project = get_env_var("GOOGLE_CLOUD_PROJECT")  # project for Vertex AI calls
location = get_env_var("GOOGLE_CLOUD_LOCATION") or "us-central1"
baseline_model = os.getenv("BASELINE_NL2SQL_MODEL", "gemini-2.5-flash")

MAX_NUM_ROWS = 80


try:
    llm_client = Client(vertexai=True, project=vertex_project, location=location)
    print(
        f"✅ Initialized Vertex AI client: project={vertex_project}, location={location}, model={baseline_model}",
        file=sys.stderr,
    )
except Exception as e:
    print("❌ Failed to initialize Vertex AI client", file=sys.stderr)
    print(repr(e), file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
    llm_client = None


def _serialize_value_for_sql(value):
    """Serializes a Python value from a pandas DataFrame into a BigQuery SQL literal."""
    if isinstance(value, (list, np.ndarray)):
        return f"[{', '.join(_serialize_value_for_sql(v) for v in value)}]"
    if pd.isna(value):
        return "NULL"
    if isinstance(value, str):
        return f"'{value.replace('\\', '\\\\').replace("'", "''")}'"
    if isinstance(value, bytes):
        return f"b'{value.decode('utf-8', 'replace').replace('\\', '\\\\').replace("'", "''")}'"
    if isinstance(value, (datetime.datetime, datetime.date, pd.Timestamp)):
        return f"'{value}'"
    if isinstance(value, dict):
        # STRUCT formatting: order must match the dataframe column order.
        return f"({', '.join(_serialize_value_for_sql(v) for v in value.values())})"
    return str(value)


database_settings = None


def get_database_settings():
    """Get database settings, caching them globally."""
    global database_settings
    if database_settings is None:
        database_settings = update_database_settings()
    return database_settings


def update_database_settings():
    """Fetch and update the database settings."""
    global database_settings
    schema_and_samples = get_bigquery_schema_and_samples()
    database_settings = {
        "bq_data_project_id": data_project,
        "bq_dataset_id": dataset_id,
        "bq_schema_and_samples": schema_and_samples,
    }
    return database_settings


def _require_envs_for_bq():
    missing = []
    if not data_project:
        missing.append("BQ_DATA_PROJECT_ID")
    if not dataset_id:
        missing.append("BQ_DATASET_ID")
    if not compute_project:
        missing.append("BQ_COMPUTE_PROJECT_ID")
    if missing:
        msg = (
            "Missing required environment variables for BigQuery connection: "
            + ", ".join(missing)
        )
        print(f"❌ {msg}", file=sys.stderr)
        raise ValueError(msg)


def get_bigquery_schema_and_samples():
    """Retrieves ONLY the schema for the BigQuery dataset tables (no samples)."""
    _require_envs_for_bq()

    client = get_bigquery_client(project=compute_project, credentials=None)
    dataset_ref = bigquery.DatasetReference(data_project, dataset_id)
    tables_context = {}
    try:
        print(
            f"🔧 Fetching schema for all tables in dataset '{dataset_id}' (project={data_project})...",
            file=sys.stderr,
        )

        table_iter = client.list_tables(dataset_ref)
        if table_iter is None:
            raise ConnectionError(
                "client.list_tables() returned None. Check BigQuery permissions and configuration."
            )

        for table in table_iter:
            table_info = client.get_table(
                bigquery.TableReference(dataset_ref, table.table_id)
            )
            table_schema = [
                (schema_field.name, schema_field.field_type)
                for schema_field in table_info.schema
            ]
            tables_context[str(table_info.full_table_id)] = {
                "table_schema": table_schema
            }

        print(
            f"✅ Successfully fetched schema for {len(tables_context)} tables.",
            file=sys.stderr,
        )

    except Exception as e:
        print("❌ Error fetching BigQuery schema:", file=sys.stderr)
        print(repr(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return f"Error fetching schema: {e}"

    return tables_context


def initial_bq_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates an initial SQL query from a natural language question."""

    prompt_template = """
You are a BigQuery SQL expert tasked with answering user's questions about BigQuery tables by generating SQL queries in the GoogleSql dialect. Your task is to write a BigQuery SQL query that answers the following question while using the provided context.

Guidelines:
- Table Referencing: Always use fully-qualified table names wrapped in backticks, e.g., `project.dataset.table`.
- Joins: Use as few joins as possible. Ensure join columns have matching types.
- Aggregations: Include all non-aggregated columns in GROUP BY.
- SQL Syntax: Produce syntactically and semantically correct BigQuery SQL. Use aliases where helpful.
- Column Usage: Only use columns that exist in the provided schema.
- Filters: Minimize returned rows using WHERE/HAVING as appropriate.
- Limit Rows: The maximum number of rows returned should be less than {MAX_NUM_ROWS}.

Schema:
{SCHEMA}

Question:
{QUESTION}

Think Step-by-Step: Carefully consider the schema, question, and best practices above to generate the correct BigQuery SQL.
"""

    try:
        # Ensure DB settings in shared state
        if "database_settings" not in tool_context.state or not tool_context.state["database_settings"]:
            tool_context.state["database_settings"] = get_database_settings()

        bq_schema_and_samples = tool_context.state["database_settings"]["bq_schema_and_samples"]
        if isinstance(bq_schema_and_samples, str):
            # Previous step failed; surface the reason
            err = f"Cannot generate SQL because schema fetching failed: {bq_schema_and_samples}"
            print(f"❌ {err}", file=sys.stderr)
            return f"Error: {err}"

        prompt = prompt_template.format(
            MAX_NUM_ROWS=MAX_NUM_ROWS,
            SCHEMA=bq_schema_and_samples,
            QUESTION=question,
        )

        if llm_client is None:
            return "Error generating SQL: Vertex AI client was not initialized."

        model_name = baseline_model
        try:
            response = llm_client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={"temperature": 0.1},
            )
        except Exception as llm_err:
            print("❌ Vertex AI call failed in initial_bq_nl2sql", file=sys.stderr)
            print(repr(llm_err), file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return f"Error generating SQL: {llm_err}"

        sql = (response.text or "").replace("```sql", "").replace("```", "").strip()
        print(f"\nGenerated SQL: {sql}", file=sys.stderr)
        tool_context.state["sql_query"] = sql
        return sql or "Error: Model returned empty SQL."

    except Exception as e:
        print("❌ Error in initial_bq_nl2sql", file=sys.stderr)
        print(repr(e), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return f"Error generating SQL: {e}"