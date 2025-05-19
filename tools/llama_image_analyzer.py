import json
import json
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from langchain_ollama import OllamaLLM
from services.vector_db import chroma_service
from config.config import config


class EnhancedLlamaVisionAnalyzer:
    """Advanced image analysis with safety checks and VectorDB integration"""

    def __init__(
        self,
        is_use_vectordb=False,
        temperature=0.1,
        top_k=30,
        top_p=0.9,
        nsfw_threshold=0.85,
    ):
        self.is_use_vectordb = is_use_vectordb
        self.llm = OllamaLLM(
            model=config.LLAMA_VISION_LLM_OLLAMA,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            num_gpu=1,
        )
        self.nsfw_threshold = nsfw_threshold

    def analyze(
        self,
        company_id: Optional[str],
        data_type: Optional[str],
        k: Optional[str],
        metadata_filter: Optional[str],
        query: Optional[str],
        search_type: Optional[str],
        image_url: str,
    ):
        if k <= 0:
            raise ValueError("k must be positive integers")

        """Comprehensive image analysis pipeline"""
        # Validate required image_url
        if not image_url:
            raise ValueError("image_url is required field")

        if self.is_use_vectordb == True:
            combined_context = ""
            # Only create context if company_id and data_type exist
            if company_id and data_type:
                try:
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

                            main_retriever = main_future.result()
                            correction_retriever = correction_future.result()
                            company_feedback_retriever = (
                                company_feedback_future.result()
                            )

                    except Exception as e:
                        raise

                    # Retrieve documents and process response
                    main_docs = main_retriever.invoke(query)
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
                        + (
                            feedback_context
                            if feedback_docs
                            else "No relevant feedback found"
                        ),
                    ]

                    combined_context = "\n\n".join(context_sections)
                except Exception as e:
                    raise

        try:
            # Build dynamic prompt
            context_block = ""
            if self.is_use_vectordb == True:
                if combined_context:
                    context_block = (
                        f"Use this contextual information:\n{combined_context}\n\n"
                    )

            prompt = f"""<start_of_turn>
            [System]
            Perform a comprehensive and advanced image analysis with confidence scores. Ensure the analysis provides not just visual details but also in-depth insights and interpretations. Specifically:

            1. **Detailed Visual Description**:
            - Describe the visual content vividly, covering settings, objects, and aesthetics.
            - Mention key visual elements, styles, and overall presentation.
            - Include spatial relationships and orientation of objects.

            2. **Advanced Graph and Chart Analysis**:
            - Detect any graphs, charts, or visual data representations (e.g., bar charts, line graphs, pie charts).
            - Classify the type of graph or chart and identify key characteristics (e.g., axes, legends, data points).
            - Extract data points, values, and trends depicted in the graph.
            - Summarize the graph's primary message or trend (e.g., marketing trends, financial growth, user demographics).
            - Identify the decision-making insights that can be drawn from the graph (e.g., future predictions, performance comparisons).
            - Provide context regarding how this data might influence business or strategic decisions.
            - Extract and present data in a structured table format with appropriate columns and rows, showing labels, values, confidence scores, and relevant metadata.

            3. **Contextual Understanding**:
            - Infer the scenario or setting depicted in the image (e.g., professional presentation, marketing analysis, social trend report).
            - Analyze possible interpretations or implications based on visual cues.
            - Estimate the intended purpose or use of the image (e.g., business reporting, data analysis, public presentation).
            - Provide potential data-driven decisions or conclusions that can be drawn from the visual content.

            4. **Text Extraction and Analysis**:
            - Extract all visible text or signage within the image.
            - Identify and transcribe textual elements with high accuracy.
            - Organize text data into structured tables with columns: "Text Content", "Confidence Score".
            - Analyze the text content for potential insights or contextual relevance.
            - Detect and analyze any textual patterns, numbers, or identifiers (e.g., dates, percentages).

            5. **Tabular Data Extraction**:
            - Detect any tabular structures present in the image (e.g., data tables, spreadsheets).
            - Accurately identify row and column structures and extract cell values.
            - Present tabular data in structured JSON format, preserving the table layout and any embedded data.
            - Perform consistency checks to ensure data integrity and accuracy.

            6. **Analytical and Decision-Making Insights**:
            - Based on the analysis, provide possible data-driven decisions or recommendations.
            - Highlight key takeaways and potential strategies that can be derived from the visual data.

            7. **Safety and Compliance Check**:
            - Verify whether the image is safe for work (SFW).
            - Identify any potentially sensitive or inappropriate content.

            Also use this context to get more relavent data: {context_block}
            
            Analyze this image:
            Image URL: {image_url}

            Return JSON response as the result : {{
                "visual_description":"",
                "graph_and_chart_analysis":"",
                "contextual_understanding":"",
                "text_extraction_and_analysis":"",
                "tabular_data_extraction":"",
                "analytical_and_decision_making_insights":"",
                "safety_and_compliance_check":"",
                "full_analysis":"based on above all factors"
            }}

            <end_of_turn>
            <start_of_turn>assistant
            """

            try:
                response = self.llm.invoke(prompt)
            except Exception as e:
                raise

            analysis_format = self._parse_response(response)

            return {
                "image_url": image_url,
                "analysis": analysis_format,
            }

        except Exception as e:
            raise

    def _parse_response(self, response):
        try:
            json_str = response.split("```json")[1].split("```")[0].strip()
            result = json.loads(json_str)

            return result
        except Exception as e:
            raise


