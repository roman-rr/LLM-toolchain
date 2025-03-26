from langchain_openai import OpenAIEmbeddings
from typing import Optional, Dict, Any

def get_openai_embeddings(
    model: str = "text-embedding-ada-002",
    dimensions: Optional[int] = None,
    **kwargs: Any
) -> OpenAIEmbeddings:
    """
    Create an OpenAI embeddings model instance.
    
    Args:
        model: The OpenAI embedding model to use
        dimensions: Optional number of dimensions for the embeddings
        **kwargs: Additional arguments to pass to the OpenAIEmbeddings constructor
    
    Returns:
        An OpenAIEmbeddings instance
    """
    return OpenAIEmbeddings(
        model=model,
        dimensions=dimensions,
        **kwargs
    )