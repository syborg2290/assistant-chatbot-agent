#!/bin/bash

# Define the FastAPI server URL
API_URL="http://localhost:9001/api/v1/crew"

# Function to log messages
log_message() {
  local message=$1
  echo "[LOG] $(date +'%Y-%m-%d %H:%M:%S') - $message"
}

# Function to create a new agent
create_agent() {
  local query=$1
  local company_id=$2
  local role=$3
  local goal=$4
  local backstory=$5
  local knowledge_sources=$6
  local extra_tools=$7

  log_message "Creating agent with query: $query, role: $role"

  response=$(curl -X 'POST' "$API_URL/create-agent" \
    -H 'Content-Type: application/json' \
    -d '{
      "query": "'"$query"'",
      "company_id": "'"$company_id"'",
      "role": "'"$role"'",
      "goal": "'"$goal"'",
      "backstory": "'"$backstory"'",
      "knowledge_sources": "'"$knowledge_sources"'",
      "extra_tools": "'"$extra_tools"'"
    }')

  echo $response
}

# Function to create a new task
create_task() {
  local company_id=$1
  local name=$2
  local description=$3
  local expected_output=$4
  local agents=$5
  local context=$6

  log_message "Creating task: $name"

  response=$(curl -X 'POST' "$API_URL/create-task" \
    -H 'Content-Type: application/json' \
    -d '{
      "company_id": "'"$company_id"'",
      "name": "'"$name"'",
      "description": "'"$description"'",
      "expected_output": "'"$expected_output"'",
      "agents": "'"$agents"'",
      "context": "'"$context"'"
    }')

  echo $response
}

# Function to create a new crew
create_crew() {
  local company_id=$1
  local agents=$2
  local tasks=$3
  local process=$4
  local full_output=$5
  local agent_manager_instructions=$6

  log_message "Creating crew with agents: $agents and tasks: $tasks"

  response=$(curl -X 'POST' "$API_URL/create-crew" \
    -H 'Content-Type: application/json' \
    -d '{
      "company_id": "'"$company_id"'",
      "agents": "'"$agents"'",
      "tasks": "'"$tasks"'",
      "process": "'"$process"'",
      "full_output": "'"$full_output"'",
      "agent_manager_instructions": "'"$agent_manager_instructions"'"
    }')

  echo $response
}

# Function to kickoff the crews
kickoff_crews() {
  local crews=$1
  local crew_inputs=$2

  log_message "Kicking off crews: $crews with inputs: $crew_inputs"

  response=$(curl -X 'POST' "$API_URL/kickoff-crews" \
    -H 'Content-Type: application/json' \
    -d '{
      "crews": "'"$crews"'",
      "crew_inputs": "'"$crew_inputs"'"
    }')

  echo $response
}

# Validate that tools and parameters are correctly configured
validate_input() {
  local tool=$1
  local param=$2
  # Here you can implement more complex validation logic
  if [[ -z "$param" ]]; then
    log_message "Error: Missing parameter for tool $tool"
    return 1
  fi
  return 0
}

# Start of the simulation script
log_message "Starting multi-agent simulation..."

# Define the company_id
COMPANY_ID="company_123"

# Create agents with dynamic tool parameters
log_message "Creating agents..."

AGENT_1=$(create_agent "Agent1_Query" "$COMPANY_ID" "Agent" "Solve complex problems in data analysis" "Background: Data scientist with 5 years of experience in AI" "KnowledgeSource1, KnowledgeSource2" "DataTool, VisualizationTool")
AGENT_2=$(create_agent "Agent2_Query" "$COMPANY_ID" "Assistant" "Assist in generating reports and analysis" "Background: Business analyst with expertise in financial forecasting" "KnowledgeSource3, KnowledgeSource4" "ReportGenTool, CalculationTool")
AGENT_3=$(create_agent "Agent3_Query" "$COMPANY_ID" "Request Handler" "Handle customer service requests and queries" "Background: Customer service experience in handling technical queries" "KnowledgeSource5" "TicketSystemTool, ResponseTool")

# Create tasks with different dependencies
log_message "Creating tasks..."

TASK_1=$(create_task "$COMPANY_ID" "Data Analysis" "Analyze raw financial data for insights" "Processed Data Insights" "[Agent1, Agent2]" "Context: Analyze financial trends for Q4")
TASK_2=$(create_task "$COMPANY_ID" "Report Generation" "Generate quarterly performance report" "Generated Report" "[Agent2, Agent3]" "Context: Include financial analysis and key KPIs")

# Create crew with tasks and agents
log_message "Creating crew..."

CREW=$(create_crew "$COMPANY_ID" "[Agent1, Agent2, Agent3]" "[Data Analysis, Report Generation]" "Process: Use data to inform business decisions" "Complete analysis and reports" "Agent Manager Instructions: Ensure high accuracy and timely delivery")

# Validate input parameters before kicking off the crew
validate_input "Agent 1" "$AGENT_1"
validate_input "Task 1" "$TASK_1"
validate_input "Task 2" "$TASK_2"

# Kickoff the crews with appropriate inputs
log_message "Kicking off the crews..."
kickoff_crews "[Crew1]" '{"ages": [29, 35, 40], "skills": ["Data analysis", "Report generation", "Customer service"], "experience_levels": ["Expert", "Intermediate", "Beginner"]}'

log_message "Multi-agent simulation completed successfully!"
