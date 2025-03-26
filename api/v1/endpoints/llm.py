from fastapi import APIRouter, HTTPException, Depends
from api.schemas.llm import LLMRequest, LLMResponse, LLMError
from api.services.llm import LLMService
import time

router = APIRouter()

@router.post("/rag/query", 
    response_model=LLMResponse,
    responses={
        500: {"model": LLMError},
        400: {"model": LLMError}
    },
    summary="Query documents using RAG",
    description="Query documents uploaded to S3 using RAG with InMemory vectorstore"
)
async def query_documents(
    request: LLMRequest,
    llm_service: LLMService = Depends(LLMService)
):
    try:
        start_time = time.time()
        
        # Process the query using the LLM service
        answer, context = await llm_service.process_rag_query(
            query=request.query,
            context_files=request.context_files,
            options=request.options,
            temperature=request.temperature
        )
        
        processing_time = time.time() - start_time
        
        return LLMResponse(
            answer=answer,
            context=context,
            metadata={
                "model": request.options.get("model_name", "gpt-4"),
                "file_count": len(request.context_files) if request.context_files else 0
            },
            processing_time=processing_time
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
