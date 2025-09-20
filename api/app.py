# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from typing import Optional, List, Dict, Any
import uvicorn
import sys
import os
from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
import asyncio

# Add the parent directory to Python path to find aimakerspace module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aimakerspace.openai_utils.chatmodel import ChatOpenAI

# Global storage for vector database
global_vector_db = None

def build_enhanced_system_message(user_message: str) -> str:
    """
    Build an aligned system message, incorporating relevant document context if available.
    The message is structured to ensure the assistant's responses are aligned with both
    the user's query and any highly relevant uploaded health records.
    """
    global global_vector_db

    base_message = (
        "You are a helpful health assistant. "
        "Only answer questions that are related to the uploaded health record. "
        "If the question is not related to the uploaded health record, "
        "say 'I'm sorry, I can only answer questions related to the uploaded health record.'"
    )

    # If no documents have been uploaded, return the base system message.
    if not global_vector_db:
        return base_message

    try:
        # Retrieve the top 5 most relevant document chunks for the user's message.
        relevant_chunks = global_vector_db.search_by_text(user_message, k=5)
        print(f"Found {len(relevant_chunks)} relevant chunks for query: {user_message}")

        # If no relevant chunks are found, return the base system message.
        if not relevant_chunks:
            print("No relevant chunks found, using base message")
            return base_message

        # If there are relevant context parts, align the system message to include them.
        if relevant_chunks:
            # Extract text from tuples (text, similarity_score)
            context_parts = [chunk[0] for chunk in relevant_chunks]
            context = "\n".join(context_parts)
            aligned_message = (
                f"{base_message}\n\n"
                "IMPORTANT: You have access to uploaded health records. "
                "Align your answer with the following relevant context when responding to the user's question:\n\n"
                f"{context}\n\n"
                "Please answer based on this context when possible."
            )
            return aligned_message

    except Exception as e:
        print(f"Error retrieving context: {e}")

    # Fallback to the base message if no context is available or an error occurs.
    return base_message


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
        
        # Build the system message
        system_message = build_enhanced_system_message(request.current_user_message)

        # Add system message
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        messages.extend(request.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": request.current_user_message})
        
        # Initialize ChatOpenAI
        chat_model = ChatOpenAI(model_name="gpt-4o-mini", api_key=request.api_key)
        
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
async def upload_pdf(file: UploadFile = File(...), api_key: str = Form(...)):
    global global_vector_db
    try:
        # Check if file was uploaded
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
            
        # Check file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Use Vercel's writable /tmp directory
        tmp_dir = "/tmp"
        
        # Read file content
        content = await file.read()
        
        # Save the uploaded file
        file_path = os.path.join(tmp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)

        # Add error handling for each major step in the PDF processing pipeline
        try:
            loader = PDFLoader(file_path)
            loader.load()
        except Exception as e:
            print(f"Error loading PDF: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load PDF: {str(e)}")

        try:
            splitter = CharacterTextSplitter()
            chunks = splitter.split_texts(loader.documents)
        except Exception as e:
            print(f"Error splitting text: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to split PDF text: {str(e)}")

        try:
            vector_db = VectorDatabase(api_key=api_key)
            global_vector_db = await vector_db.abuild_from_list(chunks)
        except Exception as e:
            print(f"Error building vector database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to build vector database: {str(e)}")

        # Clean up uploaded file
        os.remove(file_path)

        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "file_size": len(content)
        }

    except Exception as e:
        print(f"Upload error: {e}")  # Debug logging
        raise HTTPException(status_code=500, detail=str(e))


# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
