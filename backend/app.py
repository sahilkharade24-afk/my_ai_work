from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

from pdf_reader import extract_text_from_pdf
from vector_store import VectorStore
from dotenv import load_dotenv
import litellm
import os

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import BackgroundTasks


# Vector DB
vs = VectorStore()


# --- Pydantic Models for Chat ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    use_rag: bool = False


# ---------------- API ROUTES ---------------- #

@app.get("/")
def home():
    return {"message": "Backend running!"}


@app.post("/chat")
def chat(data: ChatRequest):
    history = data.history
    use_rag = data.use_rag
    
    # Get the last user question from the history
    last_user_message = next((msg.content for msg in reversed(history) if msg.role == 'user'), None)

    if not last_user_message:
        return {"answer": "I can't seem to find your question."}

    final_messages = [msg.dict() for msg in history]

    if use_rag and vs.index.ntotal > 0:
        # Search for context if RAG is enabled and documents are indexed
        context = vs.search(last_user_message)
        
        # Prepend the context as a system message
        system_message = {
            "role": "system",
            "content": f"You are a helpful assistant. Use the following context from a PDF document to answer the user's question.\n\nContext:\n{context}"
        }
        final_messages.insert(0, system_message)
    else:
        # Add a generic system message if not using RAG
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant."
        }
        final_messages.insert(0, system_message)

    response = litellm.completion(
        model="groq/llama-3.1-8b-instant",
        messages=final_messages
    )
    answer = response.choices[0].message.content
    
    return JSONResponse(content={"answer": answer})


def _process_pdf_and_update_vector_store(file_path: str):
    """
    Extracts text from a PDF and adds it to the vector store.
    This is a blocking, CPU-bound function.
    """
    text = extract_text_from_pdf(file_path)
    vs.add_text(text)


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    temp_path = "uploaded.pdf"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Run the blocking function in a background task
    background_tasks.add_task(_process_pdf_and_update_vector_store, temp_path)

    return {"message": "PDF processing started in the background."}
