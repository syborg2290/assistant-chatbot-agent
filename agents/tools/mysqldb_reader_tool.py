from crewai.tools import BaseTool
from sqlalchemy import create_engine
from utils.database_tool_helper import execute_sql_query
from utils.exceptions.custom_exceptions import CustomException


class MySQLReaderTool(BaseTool):
    """
    A tool for querying MySQL databases with integrated schema analysis.

    This tool allows execution of SQL queries on a MySQL database. It connects using
    the provided credentials and database details (host, user, password, database, and port).
    It uses SQLAlchemy to establish the connection and execute the queries.

    Parameters for `_run` method:
    - query (str): The SQL query string to be executed on the MySQL database.
    - limit (int): The maximum number of results to return from the query. Default is 100.

    Returns:
    - str: The result of the SQL query execution or an error message if the query fails.
    """

    name: str = "MySQL Database Reader"
    description: str = (
        "A tool for querying MySQL databases with integrated schema analysis. "
        "Allows execution of SQL queries and returns the results based on a specified limit."
        """
        Executes a SQL query on the MySQL database.

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
        port: int = 3306,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.connection_uri = (
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        )

    def _run(self, query: str, limit: int = 100) -> str:

        try:
            engine = create_engine(self.connection_uri)
            return execute_sql_query(engine, query, limit)
        except Exception as e:
            return CustomException(500, f"MySQL Error: {str(e)}")
