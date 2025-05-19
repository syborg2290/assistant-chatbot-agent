from crewai.tools import BaseTool
from sqlalchemy import create_engine
from utils.database_tool_helper import execute_sql_query
from utils.exceptions.custom_exceptions import CustomException


class SQLiteReaderTool(BaseTool):
    """
    Tool for querying SQLite databases.

    This tool allows users to execute SQL queries on a specified SQLite database and retrieve results efficiently.
    It supports limiting the number of returned rows to manage large result sets.
    """

    name: str = "SQLite Database Reader"
    description: str = (
        "Executes SQL queries on a specified SQLite database and returns the query results. "
        "Useful for retrieving and analyzing data stored in SQLite files."
        """
        Execute an SQL query on the SQLite database.

        Args:
            query (str): The SQL query to be executed.
                - Must be a valid SQL statement supported by SQLite.
                - Example: 'SELECT * FROM users WHERE age > 30'

            limit (int, optional): The maximum number of rows to retrieve.
                - Defaults to 100.
                - Controls the number of results returned, useful for limiting large datasets.
                - Example: 50

        Returns:
            str: The formatted result of the SQL query or an error message if execution fails.
        """
    )

    def __init__(self, db_path: str, **kwargs):

        super().__init__(**kwargs)
        self.db_path = db_path

    def _run(self, query: str, limit: int = 100) -> str:

        try:
            engine = create_engine(f"sqlite:///{self.db_path}")
            return execute_sql_query(engine, query, limit)
        except Exception as e:
            return CustomException(500, f"SQLite Error: {str(e)}")
