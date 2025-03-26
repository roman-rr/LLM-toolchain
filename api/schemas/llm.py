from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class LLMRequest(BaseModel):
    query: str = Field(..., description="The query text to process")
    context_files: Optional[List[str]] = Field(
        default=None, 
        description="List of specific file paths in S3 to use as context"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "bucket_name": "carftflow-demo",
            "prefix": "uploads/",
            "model_name": "gpt-4",
            "file_extensions": [".txt", ".pdf", ".doc"],
            "chain_options": {}
        },
        description="Additional options for LLM processing"
    )
    temperature: Optional[float] = Field(
        default=0.7, 
        description="Temperature for LLM response",
        ge=0.0,
        le=1.0
    )

class ContextDocument(BaseModel):
    content: str
    metadata: Dict[str, Any]
    source: str

class LLMResponse(BaseModel):
    answer: str
    context: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the processing"
    )
    processing_time: float = Field(
        description="Time taken to process the query in seconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of the response"
    )

class LLMError(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 