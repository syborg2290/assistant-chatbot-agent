from crewai.tools import BaseTool
from typing import Optional, Dict, List
from sqlalchemy import create_engine, inspect
from utils.exceptions.custom_exceptions import CustomException


class SQLSchemaAnalyzerTool(BaseTool):
    """
    Analyze the structure of SQL databases (PostgreSQL, MySQL, MariaDB, SQLite).

    This tool analyzes the database schema, including table structures, columns, primary keys,
    foreign keys, indexes, and relationships between tables. It provides a comprehensive overview
    of the database for schema analysis and visualization.
    """

    name: str = "SQL Schema Analyzer"
    description: str = (
        "Performs detailed analysis of SQL database schemas, including table structures, "
        "columns, primary keys, foreign keys, and inter-table relationships. Supports PostgreSQL, "
        "MySQL, MariaDB, and SQLite databases."
        """
        Analyze the database schema, optionally focusing on a specific table.

        Args:
            table_name (str, optional): The name of a specific table to analyze.
                - If provided, returns the schema of the specified table only.
                - If omitted, analyzes the entire database.
                - Example: 'users'

        Returns:
            str: A formatted schema analysis report or an error message if analysis fails.
        """
    )

    def __init__(
        self,
        db_type: str,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        db_path: Optional[str] = None,
        port: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.db_type = db_type.lower()
        self.connection_uri = self._build_connection_uri(
            host, user, password, database, db_path, port
        )

    def _run(self, table_name: Optional[str] = None) -> str:

        try:
            engine = create_engine(self.connection_uri)
            inspector = inspect(engine)

            if table_name:
                return self._analyze_table(inspector, table_name)
            return self._analyze_full_database(inspector)

        except Exception as e:
            return CustomException(500, f"Schema Analysis Error: {str(e)}")

    def _analyze_full_database(self, inspector) -> str:
        """
        Analyze the entire database structure and gather metadata.

        Args:
            inspector: SQLAlchemy inspector object to introspect the database schema.

        Returns:
            str: Formatted string representing the full database schema.
        """
        schema_info = {"tables": [], "total_tables": 0, "relationships": []}

        # Get all tables
        tables = inspector.get_table_names()
        schema_info["total_tables"] = len(tables)

        # Analyze each table
        for table in tables:
            table_info = self._get_table_details(inspector, table)
            schema_info["tables"].append(table_info)

        # Get foreign key relationships
        schema_info["relationships"] = self._get_relationships(inspector)

        return self._format_full_schema(schema_info)

    def _get_table_details(self, inspector, table_name) -> Dict:
        """
        Get detailed information about a specific table.

        Args:
            inspector: SQLAlchemy inspector object.
            table_name (str): Name of the table to analyze.

        Returns:
            dict: Dictionary containing table details including columns, primary keys, foreign keys, and indexes.
        """
        return {
            "table_name": table_name,
            "columns": inspector.get_columns(table_name),
            "primary_key": inspector.get_pk_constraint(table_name),
            "foreign_keys": inspector.get_foreign_keys(table_name),
            "indexes": inspector.get_indexes(table_name),
        }

    def _get_relationships(self, inspector) -> List:
        """
        Extract relationships between tables based on foreign key constraints.

        Args:
            inspector: SQLAlchemy inspector object.

        Returns:
            list: List of dictionaries containing relationship information between tables.
        """
        relationships = []
        for table in inspector.get_table_names():
            for fk in inspector.get_foreign_keys(table):
                relationships.append(
                    {
                        "source_table": table,
                        "target_table": fk["referred_table"],
                        "columns": fk["constrained_columns"],
                    }
                )
        return relationships

    def _format_full_schema(self, schema_info) -> str:
        """
        Format and present the complete schema information.

        Args:
            schema_info (dict): Dictionary containing metadata about tables and relationships.

        Returns:
            str: Formatted string representation of the database schema.
        """
        output = []
        output.append(f"Database Schema Analysis ({self.db_type.upper()})")
        output.append(f"Total Tables: {schema_info['total_tables']}\n")

        for table in schema_info["tables"]:
            output.append(self._format_table_info(table))

        output.append("\nTable Relationships:")
        for rel in schema_info["relationships"]:
            output.append(
                f"{rel['source_table']} -> {rel['target_table']} "
                f"via {', '.join(rel['columns'])}"
            )

        return "\n".join(output)

    def _format_table_info(self, table_info) -> str:
        """
        Format the schema information for an individual table.

        Args:
            table_info (dict): Dictionary containing detailed table metadata.

        Returns:
            str: Formatted string representation of table information.
        """
        output = []
        output.append(f"Table: {table_info['table_name']}")
        output.append("Columns:")
        for col in table_info["columns"]:
            output.append(
                f"- {col['name']}: {col['type']} "
                f"{'(PK)' if col['name'] in table_info['primary_key'].get('constrained_columns', []) else ''}"
            )

        if table_info["foreign_keys"]:
            output.append("\nForeign Keys:")
            for fk in table_info["foreign_keys"]:
                output.append(
                    f"- {', '.join(fk['constrained_columns'])} "
                    f"-> {fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )

        return "\n".join(output)
