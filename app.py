from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

# Import your chain modules
from fine_tuned_chain import create_chain as create_basic_chain
from rag_gpt_model_pdf_chain import create_chain as create_pdf_chain
from rag_gpt_model_txt_from_dir_chain import create_chain as create_txt_chain
from rag_gpt_model_pdf_pinecone_chain import create_chain as create_pinecone_chain

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LangChain API",
    description="API for various LangChain implementations",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chains (lazy loading)
chains = {}

def get_chain(chain_type: str):
    """Lazy load chains to improve startup time"""
    if chain_type not in chains:
        if chain_type == "basic":
            chains[chain_type] = create_basic_chain()
        elif chain_type == "pdf":
            chains[chain_type] = create_pdf_chain()
        elif chain_type == "txt":
            chains[chain_type] = create_txt_chain()
        elif chain_type == "pinecone":
            chains[chain_type] = create_pinecone_chain()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chain type: {chain_type}")
    return chains[chain_type]

# Request and response models
class QueryRequest(BaseModel):
    query: str
    chain_type: str = "basic"  # Default to basic chain
    options: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    answer: str
    context: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Welcome to the LangChain API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        chain = get_chain(request.chain_type)
        
        # Process the query
        result = chain.invoke({"input": request.query})
        
        # Format the response based on chain type
        if request.chain_type == "basic":
            return {
                "answer": result.content if hasattr(result, 'content') else str(result),
                "metadata": {"chain_type": request.chain_type}
            }
        else:
            # For RAG chains
            return {
                "answer": result.get("answer", "No answer provided"),
                "context": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    } for doc in result.get("context", [])
                ] if "context" in result else None,
                "metadata": {"chain_type": request.chain_type}
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 