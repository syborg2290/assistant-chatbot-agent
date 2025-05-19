from loguru import logger
from crewai import Agent, LLM
from crewai.tools import BaseTool
from typing import Optional, List, Any
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from .tools_handler import handle_extra_tools
from config.config import config
from .tools.human_tool import HumanTool


class CreateAgent:

    def step_callback(self, role: str, step_result: Any, company_id: str):
        """
        Callback function after each step of the agent's operation. It cleans up temporary files.

        Args:
            step_result (Any): The result of the step that was processed.
        """
        output_object = {"company": company_id, "output": step_result}
        logger.info(f"Agent : {role} step completed: {output_object} ")

    def init_agent(
        self,
        company_id: str,
        role: str,
        goal: str,
        backstory: str,
        max_iter: int = 20,
        max_rpm: Optional[int] = None,
        max_execution_time: Optional[int] = None,
        max_retry_limit: int = 2,
        extra_tools: Optional[List[dict]] = None,
        custom_prompt_knowledge: Optional[str] = None,
        allow_delegation: bool = False,
        allow_human_tool: bool = False,
    ) -> Agent:
        """
        Initializes the agent with the given parameters and processes the knowledge sources.

        Args:
            company_id (str): The company ID associated with the agent.
            user_id (str): The user ID for agent interaction.
            role (str): The role the agent will play.
            goal (str): The goal the agent aims to achieve.
            backstory (str): The background or context for the agent.
            max_iter (int, optional): Maximum number of iterations for agent operations.
            max_rpm (int, optional): Maximum requests per minute.
            max_execution_time (int, optional): Max execution time in seconds.
            max_retry_limit (int, optional): Maximum retry attempts for the agent.

        Returns:
            Agent: The initialized agent instance.
        """

        if custom_prompt_knowledge:
            string_source = StringKnowledgeSource(
                content=custom_prompt_knowledge,
            )

        extra_tool_instances: List[BaseTool] = []

        if extra_tools:
            # Handle extra tools separately
            extra_tool_instances = handle_extra_tools(extra_tools)

        # Conditionally append human_chat to tools if allow_human_tool is True
        # Create custom human tool instance if needed
        human_tool_instance = [HumanTool()] if allow_human_tool else []

        tools = [
            *extra_tool_instances,
            *human_tool_instance,
        ]

        try:
            # Create the agent instance
            return Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                max_iter=max_iter,
                max_rpm=max_rpm,
                max_execution_time=max_execution_time,
                memory=True,
                verbose=True,
                allow_delegation=allow_delegation,
                step_callback=lambda step_result: self.step_callback(
                    role=role, step_result=step_result, company_id=company_id
                ),
                cache=True,
                system_template="""<|start_header_id|>system<|end_header_id|>
                            {{ .System }}<|eot_id|>""",
                prompt_template="""<|start_header_id|>user<|end_header_id|>
                            {{ .Prompt }}<|eot_id|>""",
                response_template="""<|start_header_id|>assistant<|end_header_id|>
                            {{ .Response }}<|eot_id|>""",
                allow_code_execution=False,
                max_retry_limit=max_retry_limit,
                respect_context_window=True,
                code_execution_mode="safe",
                embedder={
                    "provider": config.AGENT_EMBEDDER_PROVIDER,
                    "config": {"model": config.AGENT_EMBEDDER_MODEL},
                },
                knowledge_sources=[
                    string_source,
                ],
                use_system_prompt=True,
                llm=LLM(model=config.AGENT_LLM_OLLAMA, base_url=config.OLLAMA_URL),
                function_calling_llm=LLM(
                    model=config.AGENT_FUNCTION_CALLING_LLM_OLLAMA,
                    base_url=config.OLLAMA_URL,
                ),
            )
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise

    def update_agent(self, agent: Agent, **kwargs) -> Agent:
        """
        Updates the agent attributes dynamically.

        Args:
            agent (Agent): The agent object to update.
            kwargs: Key-value pairs of attributes to update.

        Returns:
            Agent: The updated agent object.
        """
        try:
            for key, value in kwargs.items():
                setattr(agent, key, value)
            return agent
        except Exception as e:
            logger.error(f"Error updating agent attributes: {e}")
            raise
