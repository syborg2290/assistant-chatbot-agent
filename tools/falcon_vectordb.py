import time
from concurrent.futures import ThreadPoolExecutor
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from services.vector_db import chroma_service

from utils.generation_time_formatter import format_generation_time
from config.config import config


class FalconVectorDB:
    """Handles AI-powered querying using Falcon and a vector database."""

    def __init__(self):
        """Initialize AI model and retriever with default values."""
        self.qa_chain = None
        self.temperature = 0.2  # Default values
        self.top_k = 50
        self.top_p = 0.85
        self.num_gpu = 1
        self.main_retriever = None

    def _initialize_qa_chain(self):
        """Creates an AI assistant using Falcon and LangChain with current parameters."""
        template = """ <start>
        
                        You are an AI-powered assistant supporting for the clients.
                        
                        **Avoid These**:
                        - Do not provide information outside of provided data.
                        - Do not make assumptions or hallucinate details.
                        - Keep responses clear, engaging, and (user/customer)-friendly.
                        
                        Context: {context}
                        
                        ** User Query **
                        query: {input} 
                        
                    <end>
                    """

        qa_prompt = PromptTemplate(
            template=template, input_variables=["context", "input"]
        )

        llm = OllamaLLM(
            model=config.FALCON_LLM_OLLAMA,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            num_gpu=self.num_gpu,
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.main_retriever,
            chain_type_kwargs={"prompt": qa_prompt},
            return_source_documents=True,
        )

    def query(
        self,
        company_id,
        data_type,
        query,
        k=5,
        metadata_filter=None,
        search_type="similarity",
        temperature=0.2,
        top_k=50,
        top_p=0.85,
        num_gpu=1,
    ):
        if k <= 0:
            raise ValueError("k must be positive integers")

        """Executes a query with enhanced context integration and dynamic parameters."""
        # Update parameters
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p
        self.num_gpu = num_gpu

        # Reinitialize QA chain with new parameters
        self.qa_chain = self._initialize_qa_chain()

        # Retrieve documents and process response
        try:
            with ThreadPoolExecutor() as executor:
                main_future = executor.submit(
                    chroma_service.get_retriever,
                    company_id=company_id,
                    data_type=data_type,
                    k=k,
                    metadata_filter=metadata_filter,
                    search_type=search_type,
                )
                correction_future = executor.submit(
                    chroma_service.get_retriever,
                    company_id=company_id,
                    data_type="corrections",
                    k=3,
                    metadata_filter=metadata_filter,
                    search_type="mmr",
                )

                company_feedback_future = executor.submit(
                    chroma_service.get_company_feedbacks,
                    company_id=company_id,
                    query=query,
                    k=3,
                    filters=metadata_filter,
                )

                self.main_retriever = main_future.result()
                correction_retriever = correction_future.result()
                company_feedback_retriever = company_feedback_future.result()

        except Exception as e:
            raise

        # Retrieve documents and process response
        main_docs = self.main_retriever.invoke(query)
        correction_docs = correction_retriever.invoke(query)
        feedback_docs = company_feedback_retriever

        feedback_context = "\n".join(
            [
                f"Feedback {idx+1}: {doc['page_content']} (Score: {doc.get('relevance_score', 0):.2f})"
                for idx, doc in enumerate(feedback_docs)
            ]
        )

        # Build combined context with error fallbacks
        context_sections = [
            "Main Context: "
            + (
                "\n".join([d.page_content for d in main_docs])
                if main_docs
                else "No main documents found"
            ),
            "Corrections: "
            + (
                "\n".join([d.page_content for d in correction_docs])
                if correction_docs
                else "No correction data available"
            ),
            "User Feedback Insights:\n"
            + (feedback_context if feedback_docs else "No relevant feedback found"),
        ]

        combined_context = "\n\n".join(context_sections)

        # Measure generation time
        start_time = time.time()

        try:
            response = self.qa_chain.invoke(
                {"input": query, "context": combined_context}
            )
        except Exception as e:
            raise

        generation_time = time.time() - start_time

        processed_answer = self._process_response(response["result"])

        return {
            "answer": processed_answer,
            "sources": response["source_documents"],
            "generation_time": format_generation_time(generation_time),
        }

    @staticmethod
    def _process_response(answer):
        """Separates thinking process from cleaned answer."""
        return {
            "cleaned_answer": "",
            "original_answer": answer,
            "reasoning": [],
        }


# Singleton instance
falcon_vector_db = FalconVectorDB()
