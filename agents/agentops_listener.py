from loguru import logger
from crewai.utilities.events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
    ToolUsageErrorEvent,
)
from crewai.utilities.events.base_event_listener import BaseEventListener
from config.rabbitmq import RabbitMQConfig


class AgentOpsListener(BaseEventListener):
    def __init__(self):
        super().__init__()
        logger.info("AgentOpsListener initialized for agent operations listener")
        self.rabbitmq = RabbitMQConfig()

    def send_rabbitmq_event(self, queue_name, key, data):
        try:
            self.rabbitmq.send_message(queue_name, key, data)
        except Exception as e:
            logger.error(
                f"Failed to send RabbitMQ event '{key}' to queue '{queue_name}': {str(e)}"
            )

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_started(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "source": str(source),
                "crew": event.crew_name,
            }
            logger.info(f"Crew '{event.crew_name}' has started execution", data)
            self.send_rabbitmq_event("agent-ops-logs", "CrewKickoffStarted", data)

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_completed(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "crew_name": event.crew_name,
                "output": event.output,
            }
            logger.success(f"Crew '{event.crew_name}' completed successfully", data)
            self.send_rabbitmq_event("agent-ops-logs", "CrewKickoffCompleted", data)

        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_failed(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "crew_name": event.crew_name,
                "error_message": str(event.error),
            }
            logger.error(f"Crew '{event.crew_name}' failed during execution", data)
            self.send_rabbitmq_event("agent-ops-logs", "CrewKickoffFailed", data)

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_started(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "agent_id": str(event.agent.id),
                "agent_role": event.agent.role,
            }
            logger.info(f"Agent '{event.agent.role}' started execution", data)
            self.send_rabbitmq_event("agent-ops-logs", "AgentExecutionStarted", data)

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_completed(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "agent_role": event.agent.role,
                "output": event.output,
            }
            logger.success(f"Agent '{event.agent.role}' completed execution", data)
            self.send_rabbitmq_event("agent-ops-logs", "AgentExecutionCompleted", data)

        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_error(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "agent_role": event.agent.role,
                "error_message": str(event.error),
            }
            logger.error(f"Agent '{event.agent.role}' encountered an error", data)
            self.send_rabbitmq_event("agent-ops-logs", "AgentExecutionError", data)

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_started(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
            }
            logger.info(f"Task started", data)
            self.send_rabbitmq_event("agent-ops-logs", "TaskStarted", data)

        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_completed(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "result": event.output,
            }
            logger.success(f"Task completed", data)
            self.send_rabbitmq_event("agent-ops-logs", "TaskCompleted", data)

        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_failed(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "error_message": str(event.error),
            }
            logger.error(f"Task failed", data)
            self.send_rabbitmq_event("agent-ops-logs", "TaskFailed", data)

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_usage_started(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "tool_name": event.tool_name,
            }
            logger.info(f"Tool '{event.tool_name}' started usage", data)
            self.send_rabbitmq_event("agent-ops-logs", "ToolUsageStarted", data)

        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_usage_finished(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "tool_name": event.tool_name,
            }
            logger.success(f"Tool '{event.tool_name}' finished usage", data)
            self.send_rabbitmq_event("agent-ops-logs", "ToolUsageFinished", data)

        @crewai_event_bus.on(ToolUsageErrorEvent)
        def on_tool_usage_error(source, event):
            data = {
                "timestamp": event.timestamp,
                "event_type": event.type,
                "tool_name": event.tool_name,
                "error_message": str(event.error),
            }
            logger.error(f"Tool '{event.tool_name}' encountered an error", data)
            self.send_rabbitmq_event("agent-ops-logs", "ToolUsageError", data)
