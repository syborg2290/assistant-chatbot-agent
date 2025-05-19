import uuid
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, add_messages
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver

# from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain.globals import set_llm_cache
from langchain_community.cache import SQLiteCache
from typing import Annotated, List, Union, Dict
from config.config import Config
from services.chatbot_state_store import session_store
from services.vector_db import chroma_service
from utils.multi_ollama_router import MultiOllamaRouter


# Parameter	              Type	     Recommended Range	               Role

# temperature	          float	     0.2 – 0.5	                     Controls randomness. Lower = more focused.
# top_p	                  float	     0.8 – 1.0	                     Nucleus sampling — focuses on top probable tokens. Lower = safer.
# top_k	                  int	     20 – 100	                     Limits token choices to top k options. Helps remove noise.
# max_tokens	          int	     512 – 2048+	                 Maximum tokens in the output (not the prompt). Controls response length.
# presence_penalty	      float	     0.0 – 1.0	                     Penalizes repetition of new topics — helps encourage variety.
# frequency_penalty	      float	     0.0 – 1.0	                     Penalizes repetition of the same phrases — good for avoiding loops.
# stop	                  list	     e.g. ["User:", "Assistant:"]	 Forces early stopping when these tokens appear.


set_llm_cache(SQLiteCache(database_path="langchain-cache.db"))

# llm = OllamaLLM(
#     model=Config.LLAMA_CHATBOT_LLM_OLLAMA,
#     temperature=0.7,
# )


class State(Dict):
    conversation_history: Annotated[
        List[Union[HumanMessage, AIMessage, SystemMessage]], add_messages
    ]
    retrieved_context: str
    generated_response: Annotated[List[AIMessage], add_messages]
    human_feedback: Annotated[List[str], add_messages]
    feedback_count: int
    company_id: str
    user_id: str
    custom_user_instructions: str
    user_query: str
    data_type: str
    company_name: str
    company_website: str
    assistant_role: str
    assistant_name: str
    main_domains: str
    sub_domains: str
    support_contact_emails: str
    support_phone_numbers: str
    support_page_url: str
    help_center_url: str


def _execute_parallel_queries(
    query: str, company_id: str, user_id: str, data_type: str
):
    """Handle parallel query execution with proper resource management"""
    try:
        with ThreadPoolExecutor() as executor:
            # Initialize retrievers for each data type
            main_retriever_future = executor.submit(
                chroma_service.get_by_marginal_relevance,
                company_id=company_id,
                data_type=data_type,
                query=query,
            )
            correction_future = executor.submit(
                chroma_service.get_by_marginal_relevance,
                company_id=company_id,
                data_type="corrections",
                query=query,
            )
            user_feedback_future = executor.submit(
                chroma_service.get_feedback_retriever,
                company_id=company_id,
                metadata_filter={
                    "company_id": company_id,
                    "user_id": user_id,
                },
            )

            # Retrieve the retriever objects
            main_docs = main_retriever_future.result()
            correction_docs = correction_future.result()
            user_feedback_retriever = user_feedback_future.result()

            # Execute queries using the retrievers
            feedback_docs = user_feedback_retriever.invoke(query)

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
                "User Feedback Data:\n"
                + (
                    "\n".join([d.page_content for d in feedback_docs])
                    if feedback_docs
                    else "No feedback documents found"
                ),
            ]

            combined_context = "\n\n".join(context_sections)

            return combined_context

    except Exception as e:
        raise


def filter_non_empty(values):
    return {key: value for key, value in values.items() if value and value.strip()}


def model(state: State):
    try:
        feedback = (
            state["human_feedback"][-1]
            if state["human_feedback"]
            else "No feedback yet"
        )

        # Get relevant documents based on the user's current query
        relevant_documents = state.get("retrieved_context", "")

        user_instructions = {state.get("custom_user_instructions", "")}

        # Create a dictionary with all the values
        values = {
            "company_name": state.get("company_name", ""),
            "company_website": state.get("company_website", ""),
            "assistant_role": state.get("assistant_role", ""),
            "assistant_name": state.get("assistant_name", ""),
            "main_domains": state.get("main_domains", ""),
            "sub_domains": state.get("sub_domains", ""),
            "support_contact_emails": state.get("support_contact_emails", ""),
            "support_phone_numbers": state.get("support_phone_numbers", ""),
            "support_page_url": state.get("support_page_url", ""),
            "help_center_url": state.get("help_center_url", ""),
        }

        # Filter out the empty or null values
        filtered_values = filter_non_empty(values)

        # Dynamically build the prompt based on the non-empty values

        assistant_specific_prompt = (
            f"You are the assistant for {filtered_values['company_name']}.\n"
        )

        # Only append non-empty sections to the prompt
        if "assistant_role" in filtered_values and "assistant_name" in filtered_values:
            assistant_specific_prompt += f"Your role is {filtered_values['assistant_role']}, and you are known as {filtered_values['assistant_name']}.\n"
        if "company_website" in filtered_values:
            assistant_specific_prompt += (
                f"Company website: {filtered_values['company_website']}\n"
            )

        if "main_domains" in filtered_values:
            assistant_specific_prompt += f"For customer inquiries, you can use the following details:\n- Main domains (areas): These are the broad sectors or industries that company specializes in, for instance such as healthcare, finance, travel, and tourism. {filtered_values['main_domains']}\n"

        if "sub_domains" in filtered_values:
            assistant_specific_prompt += f"- Subdomains (specific areas): These refer to narrower sectors or specializations within the broader main domains. For instance, in healthcare, subdomains could include patient care, health insurance, or medical equipment. {filtered_values['sub_domains']}\n"

        if "support_contact_emails" in filtered_values:
            assistant_specific_prompt += (
                f"- Support email(s): {filtered_values['support_contact_emails']}\n"
            )
        if "support_phone_numbers" in filtered_values:
            assistant_specific_prompt += f"- Support phone number(s): {filtered_values['support_phone_numbers']}\n"
        if "support_page_url" in filtered_values:
            assistant_specific_prompt += f"For further assistance, users can visit our Support Page: {filtered_values['support_page_url']}\n"
        if "help_center_url" in filtered_values:
            assistant_specific_prompt += (
                f"Help Center: {filtered_values['help_center_url']}\n"
            )

        prompt = f"""
        **Context** (Use ONLY these sources. Supplement with foundational knowledge when necessary):
        - Conversation History: {[msg.content for msg in state['conversation_history']]}
        - Custom Instructions: {user_instructions}
        - Human Feedback: {feedback}
        - Relevant Documents: {relevant_documents}
        - Company/Assistant Info: {assistant_specific_prompt}

        **Your Task**:
        Write a direct, helpful, and human-like response that solves the user's issue or answers their question without adding extra commentary or analysis.

        **Response Guidelines**:
        Stay:
        - Clear, honest, and concise
        - Friendly and professional, but natural — talk like a real person, not a customer support script
        - Strictly within the context provided

        Do:
        - Use plain language and a conversational tone
        - Adapt your tone to match the user's style
        - Give answers without prefacing them with things like “Here’s a response to your question”
        - Only greet, thank, or sign off when it makes sense in context (not every time)
        - Offer guidance or next steps when needed — no fluff

        Avoid:
        - Meta-comments like “This response is helpful because…”, “it seems like the user…”, “human-like response…”, “Here’s a message that…”, “Based on the context…” or “Here is a direct, helpful, and human-like response that solves the user's issue:” 
        - Describing the response instead of just responding
        - Overexplaining or stating the obvious
        - Robotic phrasing, templated support lines, or generic courtesy language (“Thank you for contacting us…”)
        - Offering general help, suggestions, or resources unrelated to the context or task
        - Trying to fulfill requests outside the scope — instead, state clearly and simply when something’s out of scope
        - Emojis, filler, or anything not grounded in the context

        **Core Approach**:
        - Be direct. Be helpful. Be real.
        - Respect the user's time — don’t repeat what they already know.
        - If something’s missing, say so clearly and offer a useful next step.
        - If the user asks for something out of scope, say so clearly and don't improvise or speculate.

        **Reminder**:
        You're not writing about a response — you’re just responding.
        Never describe what you're about to say — just say it.
        Never offer unrelated help or resources for questions outside the provided context.
        Be the assistant the user would want to talk to: helpful, human, and straight to the point.
        """

        if Config.APP_ENV == "development":
            # Development environment configuration
            ollama_router = MultiOllamaRouter(["http://localhost:11434"])
        else:
            ollama_router = MultiOllamaRouter(
                [
                    "http://localhost:11434",
                    "http://localhost:11435",
                    "http://localhost:11436",
                ]
            )

        llm = ollama_router.get_next_llm()

        response = llm.invoke(
            [
                SystemMessage(
                    content="You are a helpful, empathetic, and professional AI assistant."
                ),
                HumanMessage(content=prompt),
            ]
        )
        return {
            "generated_response": [response],
            "conversation_history": state["conversation_history"] + [response],
            "human_feedback": state["human_feedback"],
            "feedback_count": state.get("feedback_count", 0) + 1,
        }
    except Exception as e:
        raise


def retrieve_node(state: State):
    retrieved_context = ""

    # Ensure the user_query is not empty or just whitespace
    if state.get("user_query", "").strip():
        # Retrieve context based on the user query and data type
        retrieved_context = _execute_parallel_queries(
            query=state["user_query"],
            company_id=state["company_id"],
            user_id=state["user_id"],
            data_type=state["data_type"],
        )

    # Save the retrieved context in the state
    state["retrieved_context"] = retrieved_context

    return {"retrieved_context": retrieved_context}


def human_node(state: State):
    return interrupt(
        {
            "generated_response": state["generated_response"][-1].content,
            "message": f"Provide feedback or type 'done' (Feedback round {state['feedback_count'] + 1}/3)",
        }
    )


def end_node(state: State):
    final_response = state["generated_response"][-1].content
    return {
        "final_response": final_response,
        "feedback_rounds": state["feedback_count"],
        "feedback_history": state["human_feedback"],
    }


graph = StateGraph(State)

# First add all nodes
graph.add_node("retrieve_node", retrieve_node)
graph.add_node("model", model)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

# Set entry point
graph.set_entry_point("retrieve_node")

# Add edges in logical order
graph.add_edge(START, "retrieve_node")  # START -> retrieve_node
graph.add_edge("retrieve_node", "model")  # retrieve_node -> model
graph.add_edge("model", "human_node")  # model -> human_node
graph.add_edge("human_node", "end_node")  # human_node -> end_node

# Set finish point
graph.set_finish_point("end_node")

# Compile
compiled_graph = graph.compile(checkpointer=MemorySaver())


def start_conversation_service(
    client_ip: str,
    message: str,
    company_id: str,
    user_id: str,
    data_type: str,
    custom_user_instructions: str,
    company_name: str,
    company_website: str,
    assistant_role: str,
    assistant_name: str,
    main_domains: str,
    sub_domains: str,
    support_contact_emails: str,
    support_phone_numbers: str,
    support_page_url: str,
    help_center_url: str,
):
    try:
        thread_id = str(uuid.uuid4())

        state = {
            "conversation_history": [HumanMessage(content=message)],
            "generated_response": [],
            "human_feedback": [],
            "feedback_count": 0,
            "company_id": company_id,
            "company_website": company_website,
            "user_id": user_id,
            "custom_user_instructions": custom_user_instructions,
            "user_query": message,
            "data_type": data_type,
            "company_name": company_name,
            "assistant_role": assistant_role,
            "assistant_name": assistant_name,
            "main_domains": main_domains,
            "sub_domains": sub_domains,
            "support_contact_emails": support_contact_emails,
            "support_phone_numbers": support_phone_numbers,
            "support_page_url": support_page_url,
            "help_center_url": help_center_url,
        }

        # Iterate through the graph stream and update state
        for chunk in compiled_graph.stream(
            state, config={"configurable": {"thread_id": thread_id}}
        ):
            for node_name, value in chunk.items():

                # Ensure to update state safely (only what's necessary)
                if node_name not in ("__interrupt__",):
                    # Merge state cautiously to avoid overwriting necessary fields
                    for key, val in value.items():
                        if key in state:
                            if isinstance(val, list):
                                state[key].extend(val)
                            else:
                                state[key] = val
                        else:
                            state[key] = val

                if node_name == "__interrupt__":
                    interrupt_obj = value[0]
                    session_store[thread_id] = state
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": True,
                        "response": interrupt_obj.value["generated_response"],
                        "message": interrupt_obj.value["message"],
                    }
                elif node_name == "end_node":
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": False,
                        "result": value,
                    }
    except Exception as e:
        print(f"Error in start_conversation_service: {e}")
        raise


def chat_service(thread_id: str, message: str):
    try:
        # logger.info(f"Chat Request -::::::::::::::: {thread_id}")
        # logger.info(f"Chat Request Session Store -::::::::::::::: {session_store}")
        if thread_id not in session_store:
            raise ValueError("Invalid thread_id")

        state = session_store[thread_id]
        state["user_query"] = message
        state["conversation_history"].append(HumanMessage(content=message))

        # Iterate through the graph stream and update state
        for chunk in compiled_graph.stream(
            state, config={"configurable": {"thread_id": thread_id}}
        ):
            for node_name, value in chunk.items():

                if node_name not in ("__interrupt__",):
                    # Safely update the state
                    for key, val in value.items():
                        if key in state:
                            if isinstance(val, list):
                                state[key].extend(val)
                            else:
                                state[key] = val
                        else:
                            state[key] = val

                if node_name == "__interrupt__":
                    interrupt_obj = value[0]
                    session_store[thread_id] = state
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": True,
                        "response": interrupt_obj.value["generated_response"],
                        "message": interrupt_obj.value["message"],
                    }
                elif node_name == "end_node":
                    session_store.pop(thread_id, None)
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": False,
                        "result": value,
                    }
    except Exception as e:
        print(f"Error in chat_service: {e}")
        raise


def feedback_service(thread_id: str, feedback: str):
    try:
        # logger.info(f"Chat Feedback Request -::::::::::::::: {thread_id}")
        # logger.info(
        #     f"Chat Feedback Request Session Store -::::::::::::::: {session_store}"
        # )

        if thread_id not in session_store:
            raise ValueError("Invalid thread_id")

        # Retrieve the current state from session store
        state = session_store[thread_id]

        state["user_query"] = feedback

        # Append the feedback to the human_feedback list
        state["human_feedback"].append(feedback)

        # Resume the conversation with the provided feedback
        for chunk in compiled_graph.stream(
            state, config={"configurable": {"thread_id": thread_id}}
        ):
            for node_name, value in chunk.items():
                if node_name not in ("__interrupt__",):
                    # Safely update the state
                    for key, val in value.items():
                        if key in state:
                            if isinstance(val, list):
                                state[key].extend(val)
                            else:
                                state[key] = val
                        else:
                            state[key] = val

                if node_name == "__interrupt__":
                    # Return the interrupt object with updated state
                    interrupt_obj = value[0]
                    session_store[thread_id] = state
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": True,
                        "response": interrupt_obj.value["generated_response"],
                        "message": interrupt_obj.value["message"],
                    }
                elif node_name == "end_node":
                    # End the conversation and clear session state
                    session_store.pop(thread_id, None)
                    return {
                        "thread_id": thread_id,
                        "requires_feedback": False,
                        "result": value,
                    }
    except Exception as e:
        print(f"Error in feedback_service: {e}")
        raise
