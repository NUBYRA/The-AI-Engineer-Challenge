# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from typing import Optional, List, Dict, Any
import uvicorn
from aimakerspace.openai_utils.chatmodel import ChatOpenAI


# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    conversation_history: List[Dict[str, Any]] = []  # For back-and-forth
    current_user_message: str
    system_message: Optional[str] = "You are a helpful assistant."
    model: Optional[str] = "gpt-4o-mini"  # Note: ChatOpenAI uses gpt-4o-mini by default
    api_key: str  # OpenAI API key for authentication

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        print(f"Debug - Starting ChatOpenAI test")
        print(f"Debug - API Key length: {len(request.api_key) if request.api_key else 0}")
        print(f"Debug - Model: {request.model}")
        
        # Build messages with conversation history
        messages = []
        
        # Add system message
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        
        # Add conversation history
        messages.extend(request.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": request.current_user_message})
        
        print(f"Debug - Messages built: {len(messages)}")
        print(f"Debug - Messages: {messages}")
        
        # Test ChatOpenAI initialization
        try:
            print("Debug - Initializing ChatOpenAI...")
            chat_model = ChatOpenAI(model_name=request.model, api_key=request.api_key)
            print("Debug - ChatOpenAI initialized successfully")
        except Exception as init_error:
            print(f"Debug - ChatOpenAI init error: {init_error}")
            return {"error": f"ChatOpenAI init failed: {str(init_error)}"}
        
        # Test the run method
        try:
            print("Debug - Calling chat_model.run...")
            response = chat_model.run(messages, text_only=True)
            print(f"Debug - Response received: {response[:100]}...")
            return {"message": response}
        except Exception as run_error:
            print(f"Debug - Run method error: {run_error}")
            return {"error": f"ChatOpenAI run failed: {str(run_error)}"}
        
    except Exception as e:
        print(f"Debug - Main error: {e}")
        return {"error": f"ChatOpenAI error: {str(e)}"}

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
