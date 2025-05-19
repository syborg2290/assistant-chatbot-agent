from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from services.crew_handler import CrewHandlerService
from dto.crew_agent_request import (
    AgentRequest,
    TaskRequest,
    CrewRequest,
    CrewInputsRequest,
)
from utils.response_handler import success_response

router = APIRouter(prefix="/crew", tags=["Multi Agents v.1"])

# Initialize the CrewHandlerService
crew_service = CrewHandlerService()


@router.post("/create-agent")
async def create_agent(request: AgentRequest):
    """Create a new agent."""
    agent = crew_service.create_agent(
        company_id=request.company_id,
        role=request.role,
        goal=request.goal,
        backstory=request.backstory,
        extra_tools=request.extra_tools,
        custom_prompt_knowledge=request.custom_prompt_knowledge,
        allow_delegation=request.allow_delegation,
        allow_human_tool=request.allow_human_tool,
    )

    return success_response(message="success", data=agent)


@router.post("/create-task")
async def create_task(request: TaskRequest):
    """Create a new task."""
    task = crew_service.create_task(
        company_id=request.company_id,
        name=request.name,
        description=request.description,
        expected_output=request.expected_output,
        agent=request.agent,
        human_input=request.human_input,
    )
    return success_response(message="success", data=task)


@router.post("/create-crew")
async def create_crew(request: CrewRequest):
    """Create a new crew."""
    crew = crew_service.create_crew(
        name=request.name,
        company_id=request.company_id,
        agents=request.agents,
        tasks=request.tasks,
        process=request.process,
        full_output=request.full_output,
        custom_prompt_knowledge=request.custom_prompt_knowledge,
    )
    return success_response(message="success", data=crew)


@router.post("/kickoff-crews")
async def kickoff_crews(request: CrewInputsRequest):
    """Kickoff crews (either synchronously or asynchronously)."""
    crews_output = crew_service.kickoff_crews(
        crews=request.crews,
        crew_inputs=request.crew_inputs,
    )

    result = jsonable_encoder(crews_output)["raw"]
    return success_response(message="success", data=result)
