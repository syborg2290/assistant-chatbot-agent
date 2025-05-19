#!/bin/bash

# Function to check if a port is already in use
# is_port_in_use() {
#     lsof -iTCP:$1 -sTCP:LISTEN -t >/dev/null 2>&1
# }

# # Start Ollama on port 11435 if not already running
# if is_port_in_use 11435; then
#     echo "Ollama is already running on port 11435."
# else
#     echo "Starting Ollama on port 11435..."
#     OLLAMA_HOST=127.0.0.1 OLLAMA_PORT=11435 ollama serve &
# fi

# # Start Ollama on port 11436 if not already running
# if is_port_in_use 11436; then
#     echo "Ollama is already running on port 11436."
# else
#     echo "Starting Ollama on port 11436..."
#     OLLAMA_HOST=127.0.0.1 OLLAMA_PORT=11436 ollama serve &
# fi

# PORT=${PORT:-9001}
# SERVER=${SERVER:-gunicorn}
# WORKERS=${WORKERS:-4}
# TIMEOUT=${TIMEOUT:-120}

# if [ -d ".venv" ]; then
#     echo "Activating virtual environment..."
#     source .venv/bin/activate
# else
#     echo "Virtual environment not found. Please create one with 'python -m venv .venv' and install dependencies."
#     exit 1
# fi

# echo "Starting the app using $SERVER on port $PORT..."

# if [ "$SERVER" == "gunicorn" ]; then
#     gunicorn start:app \
#         --workers $WORKERS \
#         --worker-class uvicorn.workers.UvicornWorker \
#         --bind 0.0.0.0:$PORT \
#         --timeout $TIMEOUT
# elif [ "$SERVER" == "uvicorn" ]; then
#     uvicorn start:app --host 0.0.0.0 --port $PORT
# else
#     echo "Invalid SERVER option. Please set SERVER to either 'gunicorn' or 'uvicorn'."
#     exit 1
# fi


# Set default port to 8000 if PORT is not set
PORT=${PORT:-9001}

# Activate your virtual environment (if necessary)
source .venv/bin/activate

# Run the FastAPI app with Gunicorn using the port from the environment variable
# gunicorn -b 0.0.0.0:$PORT start:app

# Alternatively, if you use uvicorn:
uvicorn start:app --host 0.0.0.0 --port $PORT