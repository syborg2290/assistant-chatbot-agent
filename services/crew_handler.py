import gc
import asyncio
from typing import List, Optional
from crewai import Crew
from agents.create_agent import CreateAgent
from agents.create_task import CreateTask
from agents.create_crew import CreateCrew
from services.crew_handler_sqlite_db import SqliteDataService
from loguru import logger


class CrewHandlerService:

    def __init__(self):
        super().__init__()
        self.create_agent_handler = CreateAgent()
        self.create_task_handler = CreateTask()
        self.create_crew_handler = CreateCrew()
        self.sqlite_service = SqliteDataService()

    def crew_usage(self, key, usage_metrics):
        logger.info(f"Crew usage metrics of {key} : {usage_metrics}")

    def initialize_agent(self, id):
        if id is not None:
            agent = self.sqlite_service.get(id)

            return self.create_agent_handler.init_agent(
                role=agent["role"],
                company_id=agent["company_id"],
                goal=agent["goal"],
                backstory=agent["backstory"],
                extra_tools=agent["extra_tools"],
                custom_prompt_knowledge=agent["custom_prompt_knowledge"],
            )
        return None

    def initialize_task(self, id):
        if id is not None:
            task = self.sqlite_service.get(id)
            initialized_agent = self.initialize_agent(task["agent"])

            return self.create_task_handler.init_task(
                agent=initialized_agent,
                company_id=task["company_id"],
                description=task["description"],
                expected_output=task["expected_output"],
                name=task["name"],
                async_execution=task["async_execution"],
                human_input=task["human_input"],
            )
        return None

    def initialize_crew(self, id):
        if id is not None:
            crew = self.sqlite_service.get(id)
            initialized_agents = [
                self.initialize_agent(agent_id) for agent_id in crew["agents"]
            ]

            initialized_tasks = [
                self.initialize_task(task_id) for task_id in crew["tasks"]
            ]

            return self.create_crew_handler.init_crew(
                name=crew["name"],
                company_id=crew["company_id"],
                agents=initialized_agents,
                tasks=initialized_tasks,
                full_output=crew["full_output"],
                process=crew["process"],
                custom_prompt_knowledge=crew["custom_prompt_knowledge"],
            )
        return None

    def create_agent(
        self,
        company_id: str,
        role: str,
        goal: str,
        backstory: str,
        extra_tools: Optional[List[dict]] = None,
        custom_prompt_knowledge: Optional[str] = None,
        allow_delegation: bool = False,
        allow_human_tool: bool = False,
    ) -> dict:
        """
        Create and return a new agent.
        """
        try:
            new_agent = self.create_agent_handler.init_agent(
                company_id=company_id,
                role=role,
                goal=goal,
                backstory=backstory,
                extra_tools=extra_tools,
                custom_prompt_knowledge=custom_prompt_knowledge,
                allow_human_tool=allow_human_tool,
                allow_delegation=allow_delegation,
            )

            agent_id = str(new_agent.id)

            self.sqlite_service.save(
                agent_id,
                {
                    "company_id": company_id,
                    "role": role,
                    "goal": goal,
                    "backstory": backstory,
                    "extra_tools": extra_tools,
                    "custom_prompt_knowledge": custom_prompt_knowledge,
                },
            )

            return {"agent_id": agent_id}

        except Exception as e:
            logger.error(f"Error creating agent for company {company_id}: {e}")
            raise

    def create_task(
        self,
        company_id: str,
        name: str,
        description: str,
        expected_output: str,
        agent: Optional[str],
        human_input: bool,
    ) -> dict:
        """
        Create and return a new task.
        """
        try:

            # Generate Agent objects that provided
            if agent is not None:
                agent_obj = self.initialize_agent(agent)

            new_task = self.create_task_handler.init_task(
                agent=agent_obj,
                company_id=company_id,
                description=description,
                expected_output=expected_output,
                name=name,
                async_execution=False,
                human_input=human_input,
            )

            task_id = str(new_task.id)

            self.sqlite_service.save(
                task_id,
                {
                    "agent": agent,
                    "company_id": company_id,
                    "description": description,
                    "expected_output": expected_output,
                    "name": name,
                    "async_execution": False,
                    "human_input": False,
                },
            )

            return {"task_id": task_id}
        except Exception as e:
            logger.error(f"Error creating task for company {company_id}: {e}")
            raise

    def create_crew(
        self,
        name: str,
        company_id: str,
        agents: Optional[List[str]],
        tasks: Optional[List[str]],
        process: str = "sequential",
        full_output: bool = False,
        custom_prompt_knowledge: Optional[str] = None,
    ) -> Crew:
        """
        Create and initialize a crew with customizable attributes.
        """
        try:
            # Generate Agent objects that provided
            if agents is not None:
                agent_objs = [self.initialize_agent(id) for id in agents]

            # Generate Task objects from the context (if needed)
            if tasks is not None:
                task_objs = [self.initialize_task(id) for id in tasks]

            new_crew = self.create_crew_handler.init_crew(
                name=name,
                company_id=company_id,
                agents=agent_objs,
                tasks=task_objs,
                full_output=full_output,
                process=process,
                custom_prompt_knowledge=custom_prompt_knowledge,
            )

            crew_id = str(new_crew.id)

            self.sqlite_service.save(
                crew_id,
                {
                    "name": name,
                    "company_id": company_id,
                    "agents": agents,
                    "tasks": tasks,
                    "full_output": full_output,
                    "process": process,
                    "custom_prompt_knowledge": custom_prompt_knowledge,
                },
            )

            return {"crew_id": crew_id}
        except Exception as e:
            logger.error(f"Error creating crew for company {company_id}: {e}")
            raise

    async def kickoff_async(self, crews: List[Crew], crew_inputs: List[dict]):
        """
        Kick off multiple crews asynchronously and wait for all to complete.
        """
        try:

            async def async_multiple_crews():
                tasks = []
                for crew, inputs in zip(crews, crew_inputs):
                    tasks.append(crew.kickoff_async(inputs=inputs))
                    self.crew_usage(key=crew.id, usage_metrics=crew.usage_metrics)

                results = await asyncio.gather(*tasks)

                return results

            await async_multiple_crews()
        except Exception as e:
            logger.error(f"Error during async kickoff of crews: {e}")
            raise

    def kickoff_crews(self, crews: List[str], crew_inputs: List[dict]):
        """
        Kickoff crews. If there's one crew, use normal (synchronous) kickoff.
        If there are multiple crews, use async kickoff.
        """
        try:
            # Generate Agent objects that provided
            if crews is not None:
                crew_objs = [self.initialize_crew(id) for id in crews]

            if len(crew_objs) == 1:
                crew = crew_objs[0]
                if len(crew_inputs) == 1:
                    result = crew.kickoff(inputs=crew_inputs[0])
                    self.crew_usage(key=crew.id, usage_metrics=crew.usage_metrics)
                    return result
                else:
                    result = crew.kickoff_for_each(inputs=crew_inputs)
                    self.crew_usage(key=crew.id, usage_metrics=crew.usage_metrics)
                    return result

            else:
                return asyncio.run(self.kickoff_async(crew_objs, crew_inputs))
        except Exception as e:
            logger.error(f"Error during crew kickoff: {e}")
            raise
        finally:
            gc.collect()


# Example usage:

# crew_service = CrewHandlerService()

# # Create agents
# coding_agent = crew_service.create_agent(
#     role="Python Data Analyst",
#     goal="Analyze data and provide insights using Python",
#     backstory="You are an experienced data analyst with strong Python skills.",
#     allow_code_execution=True,
# )

# # Create tasks
# task_1 = crew_service.create_task(
#     description="Analyze the first dataset and calculate the average age of participants. Ages: {ages}",
#     agent=coding_agent,
# )

# task_2 = crew_service.create_task(
#     description="Analyze the second dataset and calculate the average age of participants. Ages: {ages}",
#     agent=coding_agent,
# )

# # Create crews
# crew_1 = crew_service.create_crew(agents=[coding_agent], tasks=[task_1])

# crew_2 = crew_service.create_crew(agents=[coding_agent], tasks=[task_2])

# # Kickoff one crew normally
# crew_service.kickoff_crews(crews=[crew_1], crew_inputs=[{"ages": [25, 30, 35, 40, 45]}])

# # Kickoff multiple crews asynchronously
# crew_service.kickoff_crews(
#     crews=[crew_1, crew_2],
#     crew_inputs=[
#         {"ages": [25, 30, 35, 40, 45]},  # Input for crew_1
#         {"ages": [20, 22, 24, 28, 30]},  # Input for crew_2
#     ],
# )
