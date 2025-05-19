from crewai.tools import BaseTool
from pymongo import MongoClient
from typing import Optional, Dict, List
from utils.database_tool_helper import format_mongo_results
from utils.exceptions.custom_exceptions import CustomException


class MongoDBReaderTool(BaseTool):
    """
    Tool for querying MongoDB databases using PyMongo.

    This tool allows querying MongoDB collections across different databases.
    You can use it to search for documents in specific collections by providing
    a query and optional parameters like projections and limits.
    """

    name: str = "MongoDB Reader"
    description: str = (
        "Tool for querying MongoDB databases using PyMongo. Allows for executing "
        "queries across multiple collections, with support for projections and result limits."
        """
        Execute MongoDB query across multiple collections.

        Args:
            query (Dict): The MongoDB query to execute on each collection.
            projection (Optional[Dict], optional): Fields to include or exclude in the query result.
            limit (int, optional): The maximum number of documents to return. Defaults to 100.

        Returns:
            str: A formatted string representing the query results across all collections.
        """
    )

    def __init__(
        self,
        host: str,
        database: str,
        collections: List[str],
        port: int = 27017,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.connection_uri = self._build_connection_uri(host, port, username, password)
        self.database = database
        self.collections = collections

    def _run(
        self, query: Dict, projection: Optional[Dict] = None, limit: int = 100
    ) -> str:

        try:
            with MongoClient(self.connection_uri) as client:
                db = client[self.database]
                results = []
                # Iterate over each collection to execute the query
                for collection_name in self.collections:
                    col = db[collection_name]
                    collection_results = col.find(query, projection).limit(limit)
                    formatted_results = format_mongo_results(collection_results)
                    results.append({collection_name: formatted_results})

                # Return the combined results from all collections
                return self._format_results(results)

        except Exception as e:
            raise CustomException(500, f"MongoDB Error: {str(e)}")

    def _build_connection_uri(
        self, host: str, port: int, username: Optional[str], password: Optional[str]
    ) -> str:
        """
        Build MongoDB connection URI.

        Args:
            host (str): The host of the MongoDB server.
            port (int): The port number of the MongoDB server.
            username (Optional[str]): Optional username for authentication.
            password (Optional[str]): Optional password for authentication.

        Returns:
            str: The MongoDB connection URI.
        """
        try:
            if not host or not port:
                raise ValueError("Host and port must be specified.")

            connection_uri = (
                f"mongodb://{username}:{password}@{host}:{port}/"
                if username and password
                else f"mongodb://{host}:{port}/"
            )
            return connection_uri

        except ValueError as ve:
            raise CustomException(400, f"MongoDB Connection URI Error: {str(ve)}")
        except Exception as e:
            raise CustomException(500, f"Unexpected Error in Connection URI: {str(e)}")

    def _format_results(self, results: List[Dict]) -> str:
        """
        Format results from multiple collections into a readable string.

        Args:
            results (List[Dict]): List of results obtained from each collection.

        Returns:
            str: A formatted string displaying the results from all collections.
        """
        if not results:
            return "No results found."

        formatted_output = []
        for collection_result in results:
            for collection_name, result in collection_result.items():
                formatted_output.append(f"Results for collection: {collection_name}")
                formatted_output.append(result)

        return "\n".join(formatted_output)
