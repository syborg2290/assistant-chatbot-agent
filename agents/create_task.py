from loguru import logger
from crewai import Task, Agent
from crewai.task import TaskOutput
from typing import Optional


class CreateTask:

    @staticmethod
    def callback_function(name: str, output: TaskOutput, company_id: str):
        """
        Callback function after the task is completed.
        """
        try:
            output_object = {"company": company_id, "output": output}
            logger.info(f"Task : {name} completed output: {output_object}")
        except Exception as e:
            logger.error(f"Error in callback_function for task {name}: {e}")
            raise

    def init_task(
        self,
        company_id: str,
        description: str,
        expected_output: str,
        name: str,
        agent: Optional[Agent] = None,
        async_execution: Optional[bool] = False,
        human_input: Optional[bool] = True,
    ) -> Task:
        """
        Create a new task with customizable attributes.
        """
        try:
            return Task(
                description=description,
                expected_output=expected_output,
                name=name,
                agent=agent,
                async_execution=async_execution,
                human_input=human_input,
                callback=lambda output: self.callback_function(
                    name,
                    output,
                    company_id,
                ),
            )
        except Exception as e:
            logger.error(f"Error initializing task {name}: {e}")
            raise

    def update_task(self, task: Task, **kwargs) -> Task:
        """
        Update task attributes dynamically.
        """
        try:
            for key, value in kwargs.items():
                setattr(task, key, value)
            return task
        except Exception as e:
            logger.error(f"Error updating task {task.name}: {e}")
            raise
