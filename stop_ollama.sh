#!/bin/bash

# Define the ports used by Ollama instances
PORTS=(11435 11436)

# Function to find and kill Ollama instances running on specific ports
stop_ollama_on_port() {
    local PORT=$1
    echo "Checking for Ollama on port $PORT..."
    
    # Find the PID of the process listening on this port
    PID=$(lsof -ti tcp:$PORT)

    if [ -n "$PID" ]; then
        echo "Ollama running on port $PORT with PID $PID. Stopping..."
        kill $PID
        sleep 1
        if ps -p $PID > /dev/null; then
            echo "Process still running. Forcing termination..."
            kill -9 $PID
        fi
    else
        echo "No Ollama instance found on port $PORT."
    fi
}

# Loop through defined ports and stop Ollama
for PORT in "${PORTS[@]}"; do
    stop_ollama_on_port $PORT
done

echo "All specified Ollama instances stopped."
