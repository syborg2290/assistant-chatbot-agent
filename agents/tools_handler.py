from loguru import logger
from crewai.tools import BaseTool
from typing import Optional, List
from .tools.mongodb_reader_tool import MongoDBReaderTool
from .tools.mongodb_schema_analyzer_tool import MongoDBSchemaAnalyzerTool
from .tools.mysqldb_reader_tool import MySQLReaderTool
from .tools.postgresql_reader_tool import PostgreSQLReaderTool
from .tools.sqlitedb_reader_tool import SQLiteReaderTool
from .tools.sql_schema_analyzer_tool import SQLSchemaAnalyzerTool
from .tools.vectordb_tool import (
    CompanyFeedbackTool,
    DocumentSearchTool,
    UserFeedbackTool,
)
from .tools.content_validator_tool import ContentValidatorTool
from .tools.vision_analyzer_tool import VisionAnalyzerTool


def handle_extra_tools(extra_tools: Optional[List[dict]]) -> List[BaseTool]:
    """
    Handle extra tools by creating instances based on tool configurations.

    Args:
        extra_tools (Optional[List[dict]]): List of dictionaries containing tool names and their configurations.

    Returns:
        List[BaseTool]: A list of instantiated tool objects.
    """
    tool_instances = []

    if not extra_tools:
        return tool_instances

    for tool in extra_tools:
        try:
            for tool_name, params in tool.items():
                match tool_name:
                    case "MongoDBReaderTool":
                        tool_instances.append(
                            MongoDBReaderTool(
                                host=params.get("host"),
                                user=params.get("user"),
                                password=params.get("password"),
                                database=params.get("database"),
                                collections=params.get("collections"),
                                port=params.get("port", 27017),  # Fixed default port
                            )
                        )
                    case "MongoDBSchemaAnalyzerTool":
                        tool_instances.append(
                            MongoDBSchemaAnalyzerTool(
                                host=params.get("host"),
                                user=params.get("user"),
                                password=params.get("password"),
                                database=params.get("database"),
                                collections=params.get("collections"),
                                port=params.get("port", 27017),  # Fixed default port
                            )
                        )
                    case "MySQLReaderTool":
                        tool_instances.append(
                            MySQLReaderTool(
                                host=params.get("host"),
                                user=params.get("user"),
                                password=params.get("password"),
                                database=params.get("database"),
                                port=params.get("port", 3306),
                            )
                        )
                    case "PostgreSQLReaderTool":
                        tool_instances.append(
                            PostgreSQLReaderTool(
                                host=params.get("host"),
                                user=params.get("user"),
                                password=params.get("password"),
                                database=params.get("database"),
                                port=params.get("port", 5432),
                            )
                        )
                    case "SQLiteReaderTool":
                        tool_instances.append(
                            SQLiteReaderTool(db_path=params.get("db_path"))
                        )
                    case "SQLSchemaAnalyzerTool":
                        tool_instances.append(
                            SQLSchemaAnalyzerTool(
                                db_type=params.get("db_type"),
                                host=params.get("host"),
                                user=params.get("user"),
                                password=params.get("password"),
                                database=params.get("database"),
                                db_path=params.get("db_path"),
                                port=params.get("port"),
                            )
                        )
                    case "DocumentSearchTool":  # Fixed tool name
                        tool_instances.append(
                            DocumentSearchTool(company_id=params.get("company_id"))
                        )
                    case "CompanyFeedbackTool":
                        tool_instances.append(
                            CompanyFeedbackTool(
                                company_id=params.get("company_id"),
                            )
                        )
                    case "UserFeedbackTool":  # Fixed tool name
                        tool_instances.append(
                            UserFeedbackTool(
                                company_id=params.get("company_id"),
                            )
                        )
                    case "ContentValidatorTool":
                        tool_instances.append(
                            ContentValidatorTool(
                                risk_threshold=params.get("risk_threshold"),
                                custom_validation_rules=params.get(
                                    "custom_validation_rules"
                                ),
                            )
                        )
                    case "VisionAnalyzerTool":
                        tool_instances.append(
                            VisionAnalyzerTool(
                                is_use_vectordb=params.get("is_use_vectordb", False)
                            )
                        )
                    case _:
                        logger.warning(f"Unrecognized tool '{tool_name}' - skipping")
        except Exception as e:
            logger.error(f"Error while processing extra tools: {e}")
            raise

    return tool_instances
