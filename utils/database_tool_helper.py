from typing import List, Any
from sqlalchemy import text
from sqlalchemy.engine.base import Engine


def execute_sql_query(self, engine: Engine, query: str, limit: int) -> str:
    """Shared method for executing SQL queries"""
    with engine.connect() as conn:
        if not query.lower().startswith("select"):
            return "Only SELECT queries are allowed"

        result = conn.execute(text(f"{query} LIMIT {limit}"))
        columns = result.keys()
        rows = result.fetchall()
        return format_sql_results(rows, columns)


def format_sql_results(self, rows: List[Any], columns: List[str]) -> str:
    """Format SQL results as string"""
    if not rows:
        return "No results found"

    header = " | ".join(columns)
    separator = "-" * len(header)
    body = "\n".join(" | ".join(str(value)[:50] for value in row) for row in rows)
    return f"{header}\n{separator}\n{body}"


def format_mongo_results(self, cursor) -> str:
    """Format MongoDB results as string"""
    try:
        docs = list(cursor)
        if not docs:
            return "No documents found"

        return "\n\n".join(
            "\n".join(f"{k}: {str(v)[:100]}" for k, v in doc.items()) for doc in docs
        )
    finally:
        cursor.close()
