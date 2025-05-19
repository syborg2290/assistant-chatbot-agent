from loguru import logger
from crewai import Crew, Agent, Task, Process, LLM
from typing import Optional, List, Any
from crewai.memory import LongTermMemory
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from agents.agentops_listener import AgentOpsListener
from config.config import config


class CreateCrew:

    # def __init__(self):
    #     try:
    #         # Initialize the listener
    #         self.agentops_listener = AgentOpsListener()
    #     except Exception as e:
    #         logger.error(f"Error initializing AgentOpsListener: {e}")
    #         raise

    def step_callback(self, step_result: Any, company_id: str):
        """
        Callback function after each step of the agent's operation.

        Args:
            step_result (Any): The result of the step that was processed.
        """
        try:
            output_object = {
                "company": company_id,
                "output": step_result,
            }
            logger.info(f"Step completed: {output_object}")
        except Exception as e:
            logger.error(f"Error in step_callback: {e}")
            raise

    def task_callback(self, task_result: Any, company_id: str):
        """
        Callback function after each step of the task's operation.

        Args:
            task_result (Any): The result of the step that was processed.
        """
        try:
            output_object = {
                "company": company_id,
                "output": task_result,
            }
            logger.info(f"Task completed: {output_object}")
        except Exception as e:
            logger.error(f"Error in task_callback: {e}")
            raise

    def init_crew(
        self,
        name: str,
        company_id: str,
        tasks: List[Task],
        agents: List[Agent],
        process: str = "sequential",
        max_rpm: Optional[int] = None,
        language: Optional[str] = "English",
        language_file: Optional[str] = None,
        full_output: bool = False,
        custom_prompt_knowledge: Optional[str] = None,
    ) -> Crew:
        """
        Create and initialize a crew with customizable attributes.
        """
        try:
            process = (
                Process.sequential if process == "sequential" else Process.hierarchical
            )

            if custom_prompt_knowledge:
                string_source = StringKnowledgeSource(
                    content=custom_prompt_knowledge,
                )
            else:
                string_source = StringKnowledgeSource(
                    content="",
                )

            # Create and return the Crew object
            return Crew(
                name=name,
                tasks=tasks,
                agents=agents,
                process=process,
                max_rpm=max_rpm,
                language=language,
                language_file=language_file,
                verbose=True,
                memory=True,
                long_term_memory=LongTermMemory(
                    storage=LTMSQLiteStorage(db_path="./memory.db")
                ),
                cache=True,
                embedder={
                    "provider": config.CREW_EMBEDDER_PROVIDER,
                    "config": {"model": config.CREW_EMBEDDER_MODEL},
                },
                knowledge_sources=[
                    string_source,
                ],
                full_output=full_output,
                step_callback=lambda step_result: self.step_callback(
                    step_result=step_result,
                    company_id=company_id,
                ),
                task_callback=lambda task_result: self.task_callback(
                    task_result=task_result,
                    company_id=company_id,
                ),
                planning=True,
                manager_llm=LLM(
                    model=config.CREW_MANAGER_LLM_OLLAMA,
                    base_url=config.OLLAMA_URL,
                ),
                planning_llm=LLM(
                    model=config.CREW_PLANNING_LLM_OLLAMA,
                    base_url=config.OLLAMA_URL,
                ),
                chat_llm=LLM(
                    model=config.CREW_CHAT_LLM_OLLAMA,
                    base_url=config.OLLAMA_URL,
                ),
                output_log_file="logs/crew-agent.json",
            )
        except Exception as e:
            logger.error(f"Error initializing crew: {e}")
            raise

    def update_crew(self, crew: Crew, **kwargs) -> Crew:
        """
        Update crew attributes dynamically.
        """
        try:
            for key, value in kwargs.items():
                setattr(crew, key, value)
            return crew
        except Exception as e:
            logger.error(f"Error updating crew: {e}")
            raise
