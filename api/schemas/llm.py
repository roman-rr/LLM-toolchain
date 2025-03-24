from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class LLMRequest(BaseModel):
    query: str = Field(..., description="The query text to process")
    context_files: Optional[List[str]] = Field(default=None, description="List of file IDs to use as context")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional options for LLM processing"
    )
    max_tokens: Optional[int] = Field(default=1000, description="Maximum tokens for response")
    temperature: Optional[float] = Field(default=0.7, description="Temperature for LLM response")

class LLMResponse(BaseModel):
    answer: str
    context: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LLMError(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 