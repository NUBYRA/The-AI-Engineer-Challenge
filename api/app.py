# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from typing import Optional, List, Dict, Any
import uvicorn
import sys
import os
from aimakerspace.text_utils import PDFLoader

# Add the parent directory to Python path to find aimakerspace module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        # Check if ChatOpenAI was imported successfully
        if ChatOpenAI is None:
            raise HTTPException(status_code=500, detail="ChatOpenAI module not available")
        
        # Build messages with conversation history
        messages = []
        
        # Add system message
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        
        # Add conversation history
        messages.extend(request.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": request.current_user_message})
        
        # Initialize ChatOpenAI
        chat_model = ChatOpenAI(model_name=request.model, api_key=request.api_key)
        
        # Use async streaming method
        async def generate():
            try:
                async for chunk in chat_model.astream(messages):
                    yield chunk
            except Exception as stream_error:
                yield f"Error: {str(stream_error)}"
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Check file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save the uploaded file
        with open(f"uploads/{file.filename}", "wb") as f:
            f.write(await file.read())

        return {"message": "PDF uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
