from crewai.tools import BaseTool
from typing import Optional, Dict, List
from pymongo import MongoClient
from utils.exceptions.custom_exceptions import CustomException


class MongoDBSchemaAnalyzerTool(BaseTool):
    """
    A tool for analyzing MongoDB collection schemas.

    This tool analyzes the structure of MongoDB collections by sampling documents
    and extracting details about field types, occurrences, and sample values.

    Parameters for `_run` method:
    - sample_size (int): The number of documents to sample from each collection for analysis. Default is 50.

    Returns:
    - str: A formatted string containing the schema analysis results for the collections.
    """

    name: str = "MongoDB Schema Analyzer"
    description: str = (
        "Analyzes MongoDB collections to provide schema information such as field types, "
        "occurrences, and sample values. Supports multiple collections and returns detailed "
        "schema insights from sampled documents."
        """
        Analyzes schemas for multiple collections by sampling documents.

        Parameters:
        - sample_size (int): The number of documents to sample from each collection. Default is 50.

        Returns:
        - str: A detailed schema analysis result, including field statistics and structure.
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

    def _run(self, sample_size: int = 50) -> str:

        try:
            analysis_results = []

            with MongoClient(self.connection_uri) as client:
                db = client[self.database]

                for collection_name in self.collections:
                    col = db[collection_name]

                    # Get sample documents
                    docs = list(col.aggregate([{"$sample": {"size": sample_size}}]))

                    if not docs:
                        analysis_results.append(
                            f"No documents found in collection '{collection_name}'"
                        )
                        continue

                    schema_result = self._analyze_schema(collection_name, docs)
                    analysis_results.append(schema_result)

            return "\n\n".join(analysis_results)

        except Exception as e:
            return CustomException(500, f"MongoDB Schema Error: {str(e)}")

    def _analyze_schema(self, collection_name: str, docs: List[Dict]) -> str:
        """
        Analyzes the document structure for a single collection.

        Parameters:
        - collection_name (str): The name of the collection being analyzed.
        - docs (List[Dict]): A list of sample documents from the collection.

        Returns:
        - str: A formatted schema analysis result for the collection.
        """
        schema = {}
        field_stats = {}

        # Analyze document structure
        for doc in docs:
            self._traverse_document(doc, schema, field_stats)

        return self._format_schema(collection_name, schema, field_stats, len(docs))

    def _traverse_document(self, doc, schema, field_stats, parent_key=""):
        """
        Recursively analyzes the structure of a document.

        Parameters:
        - doc (Dict): A single document to be analyzed.
        - schema (Dict): A dictionary storing the schema information.
        - field_stats (Dict): A dictionary storing field statistics (types and occurrences).
        - parent_key (str): The parent field's key, used for nested documents.

        Updates:
        - schema: Adds information about field types and occurrences.
        - field_stats: Adds statistics about the types of fields.
        """
        for key, value in doc.items():
            full_path = f"{parent_key}.{key}" if parent_key else key
            field_type = type(value).__name__

            # Update schema
            if full_path not in schema:
                schema[full_path] = {
                    "types": set(),
                    "occurrence": 0,
                    "sample_values": set(),
                }

            schema[full_path]["types"].add(field_type)
            schema[full_path]["occurrence"] += 1
            schema[full_path]["sample_values"].add(str(value)[:50])

            # Update field statistics
            if field_type not in field_stats:
                field_stats[field_type] = {"count": 0, "fields": set()}
            field_stats[field_type]["count"] += 1
            field_stats[field_type]["fields"].add(full_path)

            # Recursive call for nested documents
            if isinstance(value, dict):
                self._traverse_document(value, schema, field_stats, full_path)

    def _format_schema(self, collection_name, schema, field_stats, sample_size) -> str:
        """
        Formats the schema analysis results into a readable string.

        Parameters:
        - collection_name (str): The name of the collection.
        - schema (Dict): The schema information for the collection.
        - field_stats (Dict): The field statistics for the collection.
        - sample_size (int): The number of documents sampled.

        Returns:
        - str: A formatted string representing the schema analysis results.
        """
        output = []
        output.append(f"MongoDB Schema Analysis ({self.database}.{collection_name})")
        output.append(f"Analyzed {sample_size} documents\n")

        output.append("Field Statistics:")
        for dtype, stats in field_stats.items():
            output.append(
                f"- {dtype}: {stats['count']} occurrences "
                f"in {len(stats['fields'])} different fields"
            )

        output.append("\nDetailed Field Structure:")
        for field, info in schema.items():
            output.append(
                f"{field}: "
                f"Types: {', '.join(info['types'])} | "
                f"Present in {info['occurrence']} docs | "
                f"Sample values: {', '.join(list(info['sample_values'])[:3])}"
            )

        return "\n".join(output)

    def _build_connection_uri(self, host, port, username, password) -> str:
        """
        Builds the MongoDB connection URI using the provided credentials.

        Parameters:
        - host (str): The host address of the MongoDB server.
        - port (int): The port on which MongoDB is running.
        - username (Optional[str]): The username for authentication.
        - password (Optional[str]): The password for authentication.

        Returns:
        - str: The connection URI to be used for connecting to MongoDB.
        """
        try:
            if not host or not port:
                raise ValueError("Host and port must be specified.")

            if username and password:
                connection_uri = f"mongodb://{username}:{password}@{host}:{port}/"
            else:
                connection_uri = f"mongodb://{host}:{port}/"

            # Test the connection string format
            if not connection_uri.startswith("mongodb://"):
                raise ValueError("Invalid MongoDB connection URI format.")

            return connection_uri

        except ValueError as ve:
            raise CustomException(400, f"MongoDB Connection URI Error: {str(ve)}")
        except Exception as e:
            raise CustomException(500, f"Unexpected Error in Connection URI: {str(e)}")
