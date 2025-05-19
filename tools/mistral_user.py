import re
import json
from concurrent.futures import ThreadPoolExecutor
from langchain_ollama import OllamaLLM
from typing import Dict, Any
from services.vector_db import chroma_service
from tools.gemma_vectordb import GemmaVectorDB
from tools.gemma_image_analyzer import EnhancedGemmaVisionAnalyzer
from config.config import config


class MistralUserHandler:
    def __init__(self):
        self.temperature = 0.2
        self.top_k = 50
        self.top_p = 0.85
        self.company_id = None
        self.user_id = None
        self.data_type = None
        self.k = None
        self.metadata_filter = {}
        self.search_type = None
        self.num_gpu = None
        self.main_retriever = None
        self.llm = OllamaLLM(
            model=config.MISTRAL_LLM_OLLAMA,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            num_gpu=self.num_gpu,
        )

    def _execute_parallel_queries(self, query: str):
        """Handle parallel query execution with proper resource management"""
        try:
            with ThreadPoolExecutor() as executor:
                # Initialize retrievers for each data type
                main_retriever_future = executor.submit(
                    chroma_service.get_retriever,
                    company_id=self.company_id,
                    data_type=self.data_type,
                    k=self.k,
                    metadata_filter=self.metadata_filter,
                    search_type=self.search_type,
                )
                user_feedback_future = executor.submit(
                    chroma_service.get_user_feedbacks,
                    company_id=self.company_id,
                    user_id=self.user_id,
                    query=query,
                    k=3,
                    filters=self.metadata_filter,
                )

                # Retrieve the retriever objects
                main_retriever = main_retriever_future.result()
                user_feedback_retriever = user_feedback_future.result()

                # Execute queries using the retrievers
                main_docs = main_retriever.invoke(query)
                feedback_docs = user_feedback_retriever

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
                    "User Feedback Insights:\n"
                    + (
                        feedback_context
                        if feedback_docs
                        else "No relevant feedback found"
                    ),
                ]

                combined_context = "\n\n".join(context_sections)

                return combined_context

        except Exception as e:
            raise

    def _generate_prompt(self, context, input) -> str:
        """Create structured prompt with clear instructions"""
        return f"""<｜begin▁of▁sentence｜>[INST] <<SYS>>

                    You are a helpful AI assistant. Analyze the query and context to determine the appropriate task type and parameters. Follow the task routing guidelines below.

                    **Task Routing Guidelines**:
                        1. **vectordb**: Use for document retrieval, similarity search, or factual queries based on the user's input.
                        2. **vision**: Use when images are mentioned or visual analysis is required. If the query refers to images, you should select this task.
                        3. **direct_response**: Use for general conversations, simple queries, or when no specific task is required (e.g., greetings, FAQ answers).
                        4. **reasoning**: Use when the input requires logical reasoning, deduction, or problem-solving, especially when multiple pieces of information need to be connected.

                        - **Important for direct_response**:
                            - Do not provide information beyond the scope of the provided context or query.
                            - Avoid making assumptions, hallucinations, or guesses.
                            - Keep responses clear, concise, and user-friendly.

                    **Response Format**:
                        task_type:<task_type>vectordb|vision|direct_response|reasoning</task_type>
                        parameters:<parameters>
                            {{
                                "query": "refined search query",  # The refined version of the user's query
                                "filters": {{}}  # Any relevant filters for the task (e.g., topic, region, etc.)
                                "image_urls": []  # If vision is chosen, include any relevant image URLs
                            }}
                        </parameters>

                    **Example**:
                    If the input is asking about retrieving documents related to a specific topic:
                    - task_type: vectordb
                    - parameters: {{"query": "retrieve documents about AI", "filters": {{"topic": "AI"}}}}

                    **Example**:
                    If the input is asking for an image-related query:
                    - task_type: vision
                    - parameters: {{"query": "analyze this image", "image_urls": ["http://example.com/image.jpg"]}}

                    **Example**:
                    If the input is a simple conversational query:
                    - task_type: direct_response
                    - parameters: {{"query": "Hello!", "filters": {{}}, "image_urls": []}}

                    **Example**:
                    If the input requires reasoning:
                    - task_type: reasoning
                    - parameters: {{"query": "explain the logical connection between X and Y", "filters": {{"topic": "logic"}}}}

                    User: Hello!
                    Assistant: Hello and welcome! 😊 How can I assist you today?

                    Context: {context}

                    **User Query**:
                    query: {input}

                [/INST]
                Assistant Response:"""

    def _generate_response_prompt(
        self,
        user_instructions,
        context,
        input,
        response,
    ) -> str:
        """Create structured prompt with clear, detailed instructions for all response types"""
        return f"""<｜begin▁of▁sentence｜>[INST] <<SYS>>

                    You are a helpful, empathetic, and professional AI assistant. 
                    Your goal is to provide **accurate**, **clear**, and **structured** 
                    responses based strictly on the user’s query and the provided context.  

                    **Instructions**:  
                    1. **Professional Tone**:  
                    - Use formal, neutral language. Avoid casual phrases (e.g., "hey", "hi", "\"hey\"").  
                    - Maintain clarity and avoid ambiguity.  

                    2. **Response Structure**:  
                    - **Answer**: Directly address the query in 1–2 concise sentences.  
                    - **Sources**: Cite sources if provided in the context (e.g., "Based on [Document X]").  
                    - **Notes**: Add clarifying details, limitations, or actionable next steps.  

                    3. **Formatting**:  
                    - Use markdown headers (e.g., **Answer**, **Sources**) to separate sections.  
                    - Avoid JSON or code blocks unless explicitly requested.  

                    4. **Context Adherence**:  
                    - Only use information from the provided context. Do not hallucinate details.  
                    - Acknowledge gaps in data with: "Additional context is required to address this fully."  

                     Please Analyze this user given instructions also: {user_instructions} 
                     
                    **Avoid**:
                    - Do not provide information **outside the context** or **the data provided**. 
                    - Avoid making **assumptions** or **hallucinating details**. If uncertain, explicitly mention the uncertainty.
                    - Do not **overcomplicate** your answer. Keep it **simple**, **straightforward**, and **accessible**.
                    - Refrain from introducing **irrelevant details** or straying from the user’s question.
                    - Avoid using overly **technical language** unless absolutely necessary. If you do, ensure you explain any complex terms in simple terms.

                    [Note]: Ensure your response is professional, engaging, and meets the user’s expectations for helpfulness. 
                    Provide clarity and empathy in your tone. Be mindful of the user's experience and tone, and aim to create a welcoming environment.

                    
                     **Response Format**:
                        {{  
                            "answer": "Direct and concise answer to the query.",  
                            "sources": ["Source 1 (e.g., report title)", "Source 2"],  
                            "notes": "Optional: Clarify gaps, ambiguities, or next steps if applicable."  
                        }}  
                        
                    <</SYS>>  
                    
                    Context: {context}

                    **User Query**:
                    query: {input}

                    **Response**: {json.dumps(response)}

                    [/INST]
                    Assistant Response:"""

    def process_response(self, response: str) -> Dict[str, Any]:
        try:
            # Extract task type using regex (adjusted to match the new response format)
            task_type_match = re.search(r"task_type:\s*(\S+)", response)
            if not task_type_match:
                raise ValueError(
                    "Model response does not contain a valid task type.",
                )
            task_type = task_type_match.group(1).strip()

            # Extract parameters using regex (adjusted for the provided format)
            params_match = re.search(r"parameters:\s*(\{.*\})", response, re.DOTALL)
            if not params_match:
                raise ValueError(
                    "Model response does not contain valid parameters.",
                )

            # Parse the parameters as JSON
            parameters = json.loads(params_match.group(1).strip())

            return {
                "task_type": task_type,
                "parameters": parameters,
                "raw_response": response,
            }
        except (AttributeError, json.JSONDecodeError) as e:
            raise

    def query(self, **kwargs):
        try:
            """Enhanced query handler with proper parameter validation"""
            # Validate required parameters
            # Define only the required parameters

            required_params = [
                "company_id",  # Required parameter for the company identifier
                "user_id",
                "query",  # Required parameter for the query input
                "data_type",  # Required parameter to define the type of data being queried
                "user_instructions",
            ]

            # Validate that the required parameters are present
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter: {param}")
                setattr(self, param, kwargs[param])

            # You can include optional parameters in kwargs if they are present
            optional_params = [
                "k",
                "metadata_filter",
                "search_type",
                "temperature",
                "top_k",
                "top_p",
                "num_gpu",
            ]

            # Validate and set optional parameters if provided
            for param in optional_params:
                if param in kwargs:
                    setattr(self, param, kwargs[param])

            user_query = kwargs["query"]
            user_instructions = kwargs["user_instructions"]

            # Execute parallel queries
            context = self._execute_parallel_queries(user_query)

            # Generate and execute prompt
            context_prompt = self._generate_prompt(context=context, input=user_query)

            context_response = self.llm.invoke(context_prompt)

            parsed_response = self.process_response(context_response)

            main_prompt = self._generate_response_prompt(
                user_instructions=user_instructions,
                context=context,
                input=user_query,
                response=self.route_task(parsed_response),
            )

            main_response = self.llm.invoke(main_prompt)

            return json.loads(main_response)

        except Exception as e:
            raise

    def route_task(self, parsed_response: Dict[str, Any]):
        """Enhanced task routing with proper validation"""
        task_type = parsed_response["task_type"]
        params = parsed_response["parameters"]

        try:
            if task_type == "vectordb":
                query_model = GemmaVectorDB()
                return query_model.query(
                    company_id=self.company_id,
                    data_type=self.data_type,
                    query=params["query"],
                    metadata_filter=params.get("filters", {}),
                    **{
                        k: getattr(self, k)
                        for k in [
                            "k",
                            "search_type",
                            "temperature",
                            "top_k",
                            "top_p",
                            "num_gpu",
                        ]
                    },
                )
            elif task_type == "vision":
                analyzer = EnhancedGemmaVisionAnalyzer(is_use_vectordb=True)

                results = []
                image_urls = (params["image_urls"],)

                for image_url in image_urls:
                    # Process through vision capabilities
                    result = analyzer.analyze(
                        company_id=self.company_id,
                        data_type=self.data_type,
                        query=params["query"],
                        metadata_filter=params.get("filters", {}),
                        **{
                            k: getattr(self, k)
                            for k in [
                                "k",
                                "search_type",
                                "temperature",
                                "top_k",
                                "top_p",
                                "num_gpu",
                            ]
                        },
                        image_url=image_url,
                    )

                    results.append(result)

                return {
                    "analysis_results": results,
                    "total_images": len(image_urls),
                    "successful_analyses": len(
                        [r for r in results if "error" not in r]
                    ),
                }
            elif task_type == "reasoning":
                query_model = GemmaVectorDB()
                return query_model.query(
                    company_id=self.company_id,
                    data_type=self.data_type,
                    query=params["query"],
                    metadata_filter=params.get("filters", {}),
                    **{
                        k: getattr(self, k)
                        for k in [
                            "k",
                            "search_type",
                            "temperature",
                            "top_k",
                            "top_p",
                            "num_gpu",
                        ]
                    },
                )
            else:
                return {"response": parsed_response["raw_response"]}

        except KeyError as e:
            raise
