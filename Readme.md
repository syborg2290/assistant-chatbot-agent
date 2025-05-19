# FastAPI AI Backend

This project is an AI backend built with FastAPI, leveraging Ollama and the Context Model protocol to interact with various tools and provide AI-powered services for the core service.

## Features
- FastAPI-based backend for AI operations
- Integration with Ollama for AI model execution
- Utilizes Context Model protocol to interact with external tools
- Lightweight and scalable architecture

## Setup

### 1. Create a Virtual Environment
To ensure dependency isolation, create and activate a virtual environment:

```sh
python -m venv .venv

python3.11 -m venv .venv
```

#### Activate the Virtual Environment
- **Linux/Mac:**
  ```sh
  source .venv/bin/activate
  ```
- **Windows:**
  ```sh
  .venv\Scripts\activate
  ```

### 2. Install Dependencies
Install the required dependencies using:

```sh
pip install -r requirements.txt
```

### 3. Save Installed Dependencies
To ensure consistency, save the installed dependencies:

```sh
pip freeze > requirements.txt
```

## Important Libraries

### 1. FastAPI Core Libraries (REST Controllers & Routing)
```sh
pip install fastapi uvicorn
```
- `fastapi` → Core framework for building APIs.
- `uvicorn` → ASGI server to run the FastAPI app.

### 2. Pydantic (Request/Response Validation)
```sh
pip install pydantic
```
- `pydantic` → Data validation and serialization.


### 3. AI Model Integration
```sh
pip install ollama
```
- `ollama` → API client for managing and querying AI models.

### 4. Logging & Monitoring
```sh
pip install loguru
```
- `loguru` → Better logging experience.

### 5. CORS & Middleware
```sh
pip install fastapi-cors
```
- `fastapi-cors` → Enables cross-origin requests.

### 6. Environment Variables Management
```sh
pip install python-dotenv
```
- `dotenv` → Loads environment variables from `.env`.

### 7. Testing
```sh
pip install pytest httpx
```
- `pytest` → For running test cases.
- `httpx` → Async client for testing FastAPI endpoints.


## Running the Server
Once dependencies are installed, run the FastAPI server:

```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

******************** Deployment & Execution **************************

Development Mode

uvicorn main:app --reload
uvicorn start:app --reload


export PORT=9001
chmod +x start.sh
./start.sh


or

APP_ENV=development python main.py

Production Mode

APP_ENV=production python main.py

or deploy with Gunicorn:

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

```

- The API will be accessible at: `http://localhost:8000`


## Run your Streamlit file

Run it in the background
Use tmux or screen so it keeps running after you log out.

With tmux:

- tmux new -s streamlit
- streamlit run app.py --server.port 8501 --server.address 0.0.0.0

- detach - ctrl + B then D

## Run it as service file

- nano /etc/systemd/system/chatbot-streamlit.service

```
[Unit]
Description=Streamlit App

[Service]
ExecStart=/root/chatbot-platform/ai-backend/chatbot_ui.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target

```

sudo systemctl start chatbot-streamlit
sudo systemctl enable chatbot-streamlit
sudo systemctl status chatbot-streamlit

'''
Install pip install vllm after activating .venv manually
 VLLM - https://docs.vllm.ai/en/latest/
'''


## License

