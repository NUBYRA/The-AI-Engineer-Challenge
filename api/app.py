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
        print(f"Received request: model={request.model}, api_key_length={len(request.api_key) if request.api_key else 0}")
        print(f"Conversation history length: {len(request.conversation_history)}")
        print(f"Current message: {request.current_user_message}")
        
        # Initialize the chat model
        chat_model = ChatOpenAI(model_name=request.model, api_key=request.api_key)
        
        # Create an async generator function for streaming responses
        async def generate():
            try:
                # Build messages from conversation history + current user message
                messages = []
                if request.system_message:
                    messages.append({"role": "system", "content": request.system_message})
                messages.extend(request.conversation_history)
                messages.append({"role": "user", "content": request.current_user_message})
                
                print(f"Built messages: {len(messages)} total")
                print(f"Messages: {messages}")
                
                # Yield each chunk of the response as it becomes available
                async for chunk in chat_model.astream(messages):
                    if chunk is not None:
                        yield chunk
                        
            except Exception as stream_error:
                print(f"Stream error: {stream_error}")
                yield f"Error: {str(stream_error)}"

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        print(f"Main error: {e}")
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
