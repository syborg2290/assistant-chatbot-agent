from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


# Enum for process types
class ProcessType(str, Enum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"


# Request model for creating an agent
class AgentRequest(BaseModel):
    company_id: str
    role: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=1, max_length=200)
    backstory: str = Field(..., min_length=1, max_length=500)
    extra_tools: Optional[List[dict]] = []
    custom_prompt_knowledge: Optional[str]
    allow_delegation: bool
    allow_human_tool: bool

    @field_validator("role", "goal", "backstory")
    def validate_non_empty(cls, value: str, field) -> str:
        if not value.strip():
            raise ValueError(f"{field.name} cannot be empty or whitespace.")
        return value


#  Example of a request to create an agent

#  {
# "company_id": "company_123",
# "role": "Customer interaction agent for software companies",
# "goal": "Interact with customers with a positive mindset, address their concerns effectively, and collect valuable customer inquiries and feedback for product improvement.",
# "backstory": "You are a well-trained AI-powered agent working for a leading SaaS solutions provider. You’ve been assisting hundreds of users across different software platforms, learning from real interactions to understand customer needs, technical challenges, and the best ways to support both technical and non-technical clients. You embody professionalism, empathy, and clarity in all interactions.",
# "custom_prompt_knowledge": "You have knowledge about various SaaS products including CRM systems, project management tools, customer support platforms, and software deployment workflows. You are familiar with the typical challenges software users face and are skilled at providing helpful responses, guiding users to the right solutions, and escalating issues when necessary."
#   "extra_tools": [
#     {
#       "VisionAnalyzerTool": {
#         "is_use_vectordb": false
#       }
#     }
#   ],
#   "allow_delegation": true,
#   "allow_human_tool": true
# }


# Request model for creating a task
class TaskRequest(BaseModel):
    company_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    expected_output: str = Field(..., min_length=1, max_length=300)
    agent: Optional[str] = (None,)
    human_input: bool

    @field_validator("name", "description", "expected_output")
    def validate_non_empty(cls, value: str, field) -> str:
        if not value.strip():
            raise ValueError(f"{field.name} cannot be empty or whitespace.")
        return value


#  Example of a request to create a task

# {
#   "company_id": "company_123",
#   "name": "Handle customer inquiries for CRM product",
#   "description": "The agent is tasked with engaging with customers who have questions or issues related to the company's CRM software. The agent should provide clear, friendly, and helpful responses, guide customers through troubleshooting steps, and collect any feedback or issues that may need escalation to the support team.",
#   "expected_output": "A complete and helpful response to the customer's inquiry, including step-by-step assistance where applicable, a friendly closing message, and a log entry of the conversation including any unresolved issues that require further support.",
#   "agent": "59ffee55-e07d-40cb-aa3e-c066dfea44ec",
#   "human_input": true
# }


# Request model for creating a crew
class CrewRequest(BaseModel):
    name: str
    company_id: str
    agents: Optional[List[str]]
    tasks: Optional[List[str]]
    process: ProcessType = ProcessType.SEQUENTIAL
    full_output: bool = False
    custom_prompt_knowledge: Optional[str] = None

    @field_validator("agents", "tasks")
    def validate_non_empty_list(cls, value: List, field) -> List:
        if not value:
            raise ValueError(f"{field.name} list cannot be empty.")
        return value


#  Example of a request to create a crew

# {
#   "name":"crewss1"
#   "company_id": "company_123",
#   "agents": [
#     "59ffee55-e07d-40cb-aa3e-c066dfea44ec"
#   ],
#   "tasks": [
#     "46aa19f5-a90b-42fa-9a65-c263d8cd6af3"
#   ],
#   "process": "sequential",
#   "full_output": false
# }


# Request model for kickoff inputs
class CrewInputsRequest(BaseModel):
    crews: List[str]
    crew_inputs: List[Dict]

    @field_validator("crews", "crew_inputs")
    def validate_non_empty_list(cls, value: List, field) -> List:
        if not value:
            raise ValueError(f"{field.name} list cannot be empty.")
        return value


#  Example of a request to kickoff crew

# {
#   "crews": [
#     "5fce6710-99e7-4bc4-beb7-184716a6fe35"
#   ],
#   "crew_inputs": [
#     {
#       "inputs" :
#       {
#          "user_ask":"Hey, how are you?",
#       }
#     }
#   ]
# }
