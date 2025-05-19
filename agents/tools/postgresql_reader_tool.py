from crewai.tools import BaseTool
from sqlalchemy import create_engine
from utils.database_tool_helper import execute_sql_query
from utils.exceptions.custom_exceptions import CustomException


class PostgreSQLReaderTool(BaseTool):
    """
    A tool for querying PostgreSQL databases using SQLAlchemy.

    This tool allows you to execute SQL queries on a PostgreSQL database by connecting
    using the provided connection details (host, user, password, database, and port).
    It utilizes SQLAlchemy to establish the connection and execute queries.

    Parameters for `_run` method:
    - query (str): The SQL query string to be executed on the PostgreSQL database.
    - limit (int): The maximum number of results to return from the query. Default is 100.

    Returns:
    - str: The result of the SQL query execution or an error message if the query fails.
    """

    name: str = "PostgreSQL Reader Tool"
    description: str = (
        "A tool for querying PostgreSQL databases using SQLAlchemy. "
        "It allows execution of SQL queries with results returned based on the specified limit."
        """
        Executes a SQL query on the PostgreSQL database.

        Parameters:
        - query (str): The SQL query string to be executed on the database.
        - limit (int): The maximum number of results to return from the query (default is 100).

        Returns:
        - str: The result of the SQL query execution or an error message if the query fails.
        """
    )

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 5432,
        **kwargs,
    ):

        super().__init__(**kwargs)
        self.connection_uri = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _run(self, query: str, limit: int = 100) -> str:

        try:
            engine = create_engine(self.connection_uri)
            return execute_sql_query(engine, query, limit)
        except Exception as e:
            return CustomException(500, f"PostgreSQL Error: {str(e)}")
