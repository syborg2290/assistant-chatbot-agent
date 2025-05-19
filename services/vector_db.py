from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction
import requests
from langchain.schema import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from loguru import logger
from pathlib import Path
from config.config import config


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="mxbai-embed-large"):
        self.model = model_name

    def __call__(self, texts):
        embeddings = []
        for text in texts:
            response = requests.post(
                f"{config.OLLAMA_URL}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            if response.ok:
                embedding = response.json()["embedding"]
                embeddings.append(embedding)
            else:
                raise ValueError(
                    f"Failed to get embedding from Ollama: {response.text}"
                )
        return embeddings


class ChromaDBService:

    def __init__(self):
        """Initialize ChromaDB client with environment-based settings"""
        try:
            self.persist_directory = config.CHROMA_DB_PATH
            self.allow_reset = config.CHROMA_ALLOW_RESET
            self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            self.embedding_function = OllamaEmbeddingFunction("mxbai-embed-large")

            db_path = Path(self.persist_directory)

            # Check if the database already exists
            if db_path.exists() and any(
                db_path.iterdir()
            ):  # Check if there is any content in the folder
                print(
                    f"[INFO] ChromaDB already exists at {self.persist_directory}. Connecting to the existing instance."
                )
            else:
                print(
                    f"[INFO] ChromaDB not found at {self.persist_directory}. Initializing a new instance."
                )

            # Initialize Chroma client
            self.client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(
                    allow_reset=self.allow_reset, anonymized_telemetry=False
                ),
            )

            self.collections = {}

        except Exception as e:
            print(f"[ERROR] Failed to initialize ChromaDB: {e}")
            raise

    def get_or_create_company_collection(self, company_id: str, data_type: str):
        """Retrieve or create a company's collection (live/test/hold/corrections)"""
        if data_type not in ["live", "test", "hold", "corrections"]:
            raise ValueError(
                "Invalid data type. Must be 'live','test' or 'hold' and 'corrections'.",
            )

        collection_name = f"company_{company_id}_{data_type}"

        try:
            if collection_name not in self.collections:
                collection = self.client.get_or_create_collection(
                    collection_name,
                    metadata={"hnsw:space": "cosine"},
                    embedding_function=self.embedding_function,
                )
                self.collections[collection_name] = collection
                logger.info(f"✅ Collection '{collection_name}' is ready.")

            return self.collections[collection_name]
        except Exception as e:
            raise

    def add_documents_to_collection_langchain(
        self, company_id: str, data_type: str, documents: list[dict]
    ):
        """
        Adds new documents to the specified ChromaDB collection.

        :param company_id: The ID of the company.
        :param data_type: The collection type ('live', 'test', 'hold', 'corrections').
        :param documents: A list of dictionaries with 'content' and 'metadata'.
        :return: Success message.
        """
        try:
            # Get or create the collection
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Convert documents into LangChain Document format
            docs = [
                Document(
                    page_content=doc["page_content"],
                    metadata={**doc.get("metadata", {}), "id": doc["id"]},
                )
                for doc in documents
            ]

            # Store documents in Chroma
            Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                collection_name=collection.name,
                persist_directory=self.persist_directory,
            )

            return {"message": "Documents successfully added."}

        except Exception as e:
            raise

    def get_by_marginal_relevance(self, company_id: str, data_type: str, query: str):
        try:
            collection = self.get_or_create_company_collection(company_id, data_type)
            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
            )

            results = vector_store.max_marginal_relevance_search_by_vector(
                embedding=self.embeddings.embed_query(query),
                k=10,
                fetch_k=100,
                lambda_mult=0.5,
            )

            return results

        except Exception as e:
            raise

    def get_retriever(
        self,
        company_id: str,
        data_type: str,
        metadata_filter: dict = None,
        search_type: str = "mmr",  # similarity(default), similarity_score_threshold, mmr
    ):
        """Return a LangChain BaseRetriever for querying documents."""
        try:
            collection = self.get_or_create_company_collection(company_id, data_type)

            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
            )

            return vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={
                    "k": 100,
                    **({"filter": metadata_filter} if metadata_filter else {}),
                },
            )

        except Exception as e:
            raise

    def query_with_langchain(
        self,
        company_id: str,
        query: str,
        data_type: str,
        k: int = 5,
        metadata_filter: dict = {},
        search_type: str = "similarity",
    ):
        """
        Query documents using LangChain's Chroma retriever with MMR-based search.

        :param company_id: The ID of the company.
        :param query: The query string.
        :param data_type: The collection type ('live', 'test', 'hold', 'corrections').
        :param k: The number of final results to return.
        :param metadata_filter: Dictionary of metadata filters (e.g., {"source": "news"}).
        :return: List of retrieved document metadata.
        """
        try:
            # Get or create the collection
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Convert ChromaDB collection to LangChain Chroma
            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
            )

            # """ Similarity Search: If a user liked a specific movie, the system will recommend movies that are highly similar to the one they liked. """

            # """ MMR Search: The system might recommend movies that are similar to the one the user liked but will also add diverse recommendations,
            #     such as different genres, actors, or themes, to give the user a broader selection. """

            # Configure retriever

            retriever = vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={
                    "k": k,
                    **({"filter": metadata_filter} if metadata_filter else {}),
                },
            )

            # Invoke the retriever
            results = retriever.get_relevant_documents(query)

            # If no results found, return an empty array
            if not results:
                print("No results found.")
                return []

            return [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in results
            ]

        except Exception as e:
            raise

    def delete_documents_from_collection_langchain_metadata(
        self, company_id: str, data_type: str, metadata_filter: dict
    ):
        """
        Deletes documents from a ChromaDB collection based on metadata filters.

        :param company_id: The ID of the company.
        :param data_type: The collection type ('live', 'test', 'hold', 'corrections').
        :param metadata_filter: Dictionary of metadata conditions (e.g., {"source": "news"}).
        :return: Success message.
        """
        try:
            # Get collection
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Apply filter to delete specific documents
            collection.delete(where=metadata_filter)

            return {"message": "Documents successfully deleted."}

        except Exception as e:
            raise

    def delete_document(self, company_id: str, metadata_id: str, data_type: str):
        """Delete a document from the specified company's collection using metadata['id']"""
        try:
            # Get or create the collection metadata
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Load vector store
            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

            # Search for the document's vector ID via metadata["id"]
            results = vector_store._collection.get(include=["metadatas", "ids"])
            matching_ids = [
                doc_id
                for doc_id, meta in zip(results["ids"], results["metadatas"])
                if meta.get("id") == metadata_id
            ]

            if not matching_ids:
                raise ValueError(
                    f"Document with metadata id '{metadata_id}' not found."
                )

            # Delete using the actual vector ID
            vector_store.delete(ids=matching_ids)

            logger.info(
                f"✅ Document with metadata ID '{metadata_id}' deleted from '{company_id}' ({data_type})"
            )
            return {
                "status": "success",
                "message": f"Document with metadata ID '{metadata_id}' deleted from '{company_id}' ({data_type})",
            }

        except Exception as e:
            logger.error(f"❌ Failed to delete document: {e}")
            raise

    def list_all_documents_in_collection_langchain(
        self, company_id: str, data_type: str
    ):
        """
        Lists all documents stored in a ChromaDB collection.

        :param company_id: The ID of the company.
        :param data_type: The collection type ('live', 'test', 'hold', 'corrections').
        :return: List of document metadata.
        """
        try:
            # Get collection
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Fetch all documents
            docs = collection.get(include=["documents"])
            metadatas = collection.get(include=["metadatas"])
            # embeddings = collection.get(include=["embeddings"])

            # Prepare return structure with safe data types
            results = []
            for i in range(len(docs["documents"])):
                results.append(
                    {
                        "id": docs["ids"][i],
                        "page_content": docs["documents"][i],
                        "metadatas": metadatas["metadatas"][i],
                        # "embeddings": embeddings["embeddings"][i],
                    }
                )

            return results

        except Exception as e:
            raise

    def list_all_collections(self):
        """List all available collections"""
        try:
            # List all collections; this now returns collection names only in Chroma v0.6.0
            collection_names = self.client.list_collections()

            # Return the list of collection names
            return collection_names  # This will now be a list of collection names

        except Exception as e:
            print(f"[ERROR] Failed to list collections: {e}")
            raise

    def delete_company_collection(self, company_id: str):
        """Delete live,test and hold collections for a company"""
        for data_type in ["live", "test", "hold", "corrections"]:
            collection_name = f"company_{company_id}_{data_type}"
            try:
                self.client.delete_collection(collection_name)
                logger.info(f"✅ Collection '{collection_name}' deleted.")
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to delete collection '{collection_name}': {str(e)}"
                )
                raise

        return {
            "status": "success",
            "message": f"All collections for company '{company_id}' deleted.",
        }

    def update_document_metadata_langchain(
        self, company_id: str, data_type: str, metadata_id: str, new_metadata: dict
    ):
        """
        Updates metadata of a document in ChromaDB using metadata['id'].
        """
        try:
            # Get collection
            collection = self.get_or_create_company_collection(company_id, data_type)

            # Load vector store
            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

            # Get all metadata and find matching vector ID
            results = vector_store._collection.get(
                include=["metadatas", "ids", "documents"]
            )
            matched_index = next(
                (
                    i
                    for i, meta in enumerate(results["metadatas"])
                    if meta.get("id") == metadata_id
                ),
                None,
            )

            if matched_index is None:
                raise ValueError(
                    f"Document with metadata id '{metadata_id}' not found."
                )

            vector_id = results["ids"][matched_index]
            document_content = results["documents"][matched_index]

            # Delete old entry
            vector_store.delete(ids=[vector_id])

            # Add new with updated metadata
            vector_store._collection.add(
                documents=[document_content],
                metadatas=[new_metadata],
                ids=[vector_id],
            )

            logger.info(
                f"✅ Metadata for document with metadata ID '{metadata_id}' updated."
            )
            return {
                "status": "success",
                "message": f"Metadata for document with metadata ID '{metadata_id}' updated in '{company_id}' ({data_type})",
            }

        except Exception as e:
            logger.error(f"❌ Failed to update metadata: {e}")
            raise

    def _get_feedback_collection_name(self, company_id: str) -> str:
        """Generate standardized feedback collection name"""
        return f"company_{company_id}_feedback"

    def get_or_create_feedback_collection(self, company_id: str):
        """Get or create specialized collection for user feedback"""
        collection_name = self._get_feedback_collection_name(company_id)

        try:
            if collection_name not in self.collections:
                collection = self.client.get_or_create_collection(
                    collection_name,
                    metadata={
                        "hnsw:space": "cosine",
                        "purpose": "user_feedback_storage",
                    },
                )
                self.collections[collection_name] = collection
                logger.info(f"✅ Feedback collection '{collection_name}' initialized")

            return self.collections[collection_name]
        except Exception as e:
            raise

    def add_chat_feedback(
        self,
        company_id: str,
        user_id: str,
        chat_content: str,
        feedback_type: str,
        feedback_reason: str,
        additional_metadata: dict = None,
    ) -> dict:
        """
        Store chat interaction with user feedback in vector database

        :param company_id: Organization identifier
        :param user_id: Unique user identifier
        :param chat_content: Full text of the chat interaction
        :param feedback_type: 'positive' or 'negative'
        :param feedback_reason: User-provided reason for feedback
        :param additional_metadata: Optional extra context
        :return: Operation status
        """
        try:
            # Validate feedback parameters
            if feedback_type.lower() not in ["positive", "negative"]:
                raise ValueError(
                    "Invalid feedback type. Must be 'positive' or 'negative'"
                )

            # Construct metadata payload
            metadata = {
                "company_id": str(company_id),
                "user_id": str(user_id),
                "feedback_type": feedback_type.lower(),
                "feedback_reason": feedback_reason,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "user_feedback",
                **(
                    {"additional_metadata": additional_metadata}
                    if additional_metadata
                    else {}
                ),
            }

            # Create document structure
            document = {"page_content": chat_content, "metadata": metadata}

            # Get feedback-specific collection
            collection = self.get_or_create_feedback_collection(company_id)

            # Store using LangChain integration
            Chroma.from_documents(
                documents=[Document(**document)],
                embedding=self.embeddings,
                collection_name=collection.name,
                persist_directory=self.persist_directory,
            )

            logger.info(
                f"✅ Feedback stored for user {user_id} in company {company_id}"
            )
            return {"status": "success", "message": "Feedback recorded"}

        except Exception as e:
            logger.error(f"Feedback storage failed: {str(e)}")
            raise

    @staticmethod
    def convert_to_chroma_filter(metadata_filter: dict) -> dict:
        if not metadata_filter:
            return {}
        return {
            "$and": [{key: {"$eq": value}} for key, value in metadata_filter.items()]
        }

    def get_feedback_retriever(
        self,
        company_id: str,
        metadata_filter: dict = None,
        search_type: str = "mmr",  # similarity_score_threshold, mmr, similarity
    ):
        """Create retriever optimized for feedback analysis"""
        try:
            collection = self.get_or_create_feedback_collection(company_id)

            vector_store = Chroma(
                client=self.client,
                collection_name=collection.name,
                embedding_function=self.embeddings,
            )

            filter_query = self.convert_to_chroma_filter(metadata_filter)

            return vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={
                    "k": 10,
                    "filter": filter_query,
                },
            )
        except Exception as e:
            raise

    def analyze_feedback(
        self, company_id: str, query: str = None, filters: dict = None, k: int = 10
    ) -> list:
        """
        Retrieve and analyze stored feedback with optional filters

        :param company_id: Organization identifier
        :param query: Semantic search query
        :param filters: Metadata filters
        :param k: Number of results to return
        :return: Processed feedback results
        """
        try:
            retriever = self.get_feedback_retriever(
                company_id=company_id,
                metadata_filter=filters if filters not in [None, {}] else None,
                k=k,
            )

            results = retriever.invoke(query or "user feedback analysis")

            return [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": doc.metadata.get("score", 0),
                }
                for doc in results
            ]
        except Exception as e:
            raise

    def delete_user_feedback(self, company_id: str, user_id: str) -> dict:
        """Remove all feedback entries for a specific user"""
        try:
            collection = self.get_or_create_feedback_collection(company_id)
            collection.delete(where={"user_id": str(user_id)})

            logger.info(
                f"🗑️ Deleted feedback for user {user_id} in company {company_id}"
            )
            return {"status": "success", "deleted_count": user_id}
        except Exception as e:
            raise

    def get_company_feedbacks(
        self,
        company_id: str,
        query: str,
        k: int = 20,
        filters: dict = None,
    ) -> list:
        """
        Retrieve all feedback entries for a specific company

        :param company_id: Target organization ID
        :param k: Number of results to return (default: 20)
        :param filters: Additional metadata filters
        :return: List of feedback entries with scores

        """
        try:
            # Base conditions with explicit operators
            base_conditions = [{"company_id": {"$eq": str(company_id)}}]

            # Add additional filters if present
            if filters:
                base_conditions.append(filters)

            # Only use $and if we have multiple conditions
            final_filter = (
                {"$and": base_conditions}
                if len(base_conditions) > 1
                else base_conditions[0]
            )

            return self.analyze_feedback(
                company_id=company_id,
                query=query,
                filters=final_filter if final_filter != {} else None,
                k=k,
            )
        except Exception as e:
            raise

    def get_user_feedbacks(
        self,
        company_id: str,
        user_id: str,
        query: str,
        k: int = 10,
        filters: dict = None,
    ) -> list:
        """
        Retrieve specific user's feedback within a company

        :param company_id: Organization ID
        :param user_id: Target user identifier
        :param k: Number of results to return
        :param filters: Additional metadata filters
        :return: List of user's feedback entries

        """
        try:
            # Base conditions with explicit operators
            base_conditions = [
                {"company_id": {"$eq": str(company_id)}},
                {"user_id": {"$eq": str(user_id)}},
            ]

            # Add additional filters if present
            if filters:
                base_conditions.append(filters)

            # Construct final filter
            final_filter = (
                {"$and": base_conditions}
                if len(base_conditions) > 1
                else base_conditions[0]
            )

            return self.analyze_feedback(
                company_id=company_id,
                query=query,
                filters=final_filter if final_filter != {} else None,
                k=k,
            )
        except Exception as e:
            raise


# Singleton instance
chroma_service = ChromaDBService()
