from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from contextlib import asynccontextmanager
import shutil
import uuid

from vector import (
    fetch_data_from_table,
    create_vector_store_from_sql_data,
    retrieve_relevant_documents_with_scores,
    generate_response_with_rag,
    analyze_infographic,
    save_feedback,
)

class Query(BaseModel):
    text: str
    top_k: Optional[int] = 3
    model: Optional[str] = "gemini-pro"
    language: Optional[str] = "English" 

class Document(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None

class Response(BaseModel):
    answer: str
    sources: Optional[List[Document]] = None

class InsightResponse(BaseModel):
    insights: str

class Feedback(BaseModel):
    question: str
    model_answer: str
    rating: float
    comments: Optional[str] = None

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

vector_store = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store
    try:
        print("Loading data from Cloud SQL...")
        documents = fetch_data_from_table()
        
        if not documents:
            print("No data found in table.")
        else:
            print("Creating/loading FAISS index...")
            embeddings_model_name = "textembedding-gecko@latest"
            vector_store = create_vector_store_from_sql_data(documents, embeddings_model_name)
            print("Vector store loaded successfully")
    except Exception as e:
        print(f"Error loading vector store: {e}")
    
    yield
    
    print("Cleaning up resources...")
    for file in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

app = FastAPI(
    title="ESG RAG API with Gemini",
    description="API for Retrieval Augmented Generation system using Gemini and FAISS",
    version="1.0.0",
    lifespan=lifespan
)

def get_vector_store():
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store is not available")
    return vector_store

@app.get("/health", tags=["system"])
async def health_check():
    """
    Check API health status.
    """
    return {
        "status": "healthy",
        "vector_store_loaded": vector_store is not None
    }

@app.post("/refresh", tags=["administration"])
async def refresh_vector_store():
    """
    Refresh the vector store by reloading data from the database.
    """
    global vector_store
    try:
        documents = fetch_data_from_table()
        if not documents:
            raise HTTPException(status_code=404, detail="No data found in table")
        
        embeddings_model_name = "textembedding-gecko@latest"
        vector_store = create_vector_store_from_sql_data(documents, embeddings_model_name)
        return {
            "status": "success",
            "message": "Vector store refreshed successfully",
            "document_count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing vector store: {str(e)}")

@app.post("/query", response_model=Response, tags=["rag"])
async def query_rag(query: Query, vs=Depends(get_vector_store)):
    """
    Perform RAG (Retrieval Augmented Generation) query.
    """
    try:
        relevant_docs, scores = retrieve_relevant_documents_with_scores(query.text, vs, query.top_k)
        
        system_instruction = ""
        if query.language == "Français":
            system_instruction = "Réponds toujours en français, quelle que soit la langue de la question."
        elif query.language == "Arabic":
            system_instruction = "أجب دائمًا باللغة العربية، بغض النظر عن لغة السؤال."
            
        modified_query = query.text
        if system_instruction:
            modified_query = f"{system_instruction}\n\n{query.text}"
            
        response = generate_response_with_rag(modified_query, vs, query.model)
        
        sources = []
        for i, doc in enumerate(relevant_docs):
            sources.append(Document(
                content=doc.page_content,
                metadata=doc.metadata,
                score=scores[i]
            ))
        
        return Response(
            answer=response.content,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/similar-documents", tags=["retrieval"])
async def get_similar_documents(query: Query, vs=Depends(get_vector_store)):
    """
    Retrieve the most similar documents to the query without generating a response.
    """
    try:
        relevant_docs, scores = retrieve_relevant_documents_with_scores(query.text, vs, query.top_k)
        
        result = []
        for i, doc in enumerate(relevant_docs):
            result.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": scores[i]
            })
        
        return {"status": "success", "documents": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.post("/analyze-image", response_model=InsightResponse, tags=["vision"])
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an infographic or image related to ESG topics using Gemini Pro Vision.
    """
    try:
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        insights = analyze_infographic(file_path)
        
        # Clean up uploaded file
        try:
            os.unlink(file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up file {file_path}: {cleanup_error}")
        
        return InsightResponse(insights=insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

@app.post("/submit-feedback", tags=["feedback"])
async def submit_feedback(feedback: Feedback):
    """
    Submit user feedback about the model's response.
    """
    try:
        save_feedback(
            feedback.question,
            feedback.model_answer,
            feedback.rating,
            feedback.comments
        )
        return {"status": "success", "message": "Feedback submitted successfully!"}
    except Exception as e:
        print(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)