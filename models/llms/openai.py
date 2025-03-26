from langchain_openai import ChatOpenAI
from typing import Optional, Dict, Any

def get_openai_chat_model(
    model_name: str = "gpt-4",
    temperature: float = 0.4,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    callbacks: Optional[list] = None,
    **kwargs: Any
) -> ChatOpenAI:
    """
    Create an OpenAI chat model instance with the specified parameters.
    
    Args:
        model_name: The OpenAI model to use (e.g., "gpt-4", "gpt-3.5-turbo")
        temperature: Controls randomness. Lower values are more deterministic.
        max_tokens: Maximum number of tokens to generate
        streaming: Whether to stream the response
        callbacks: List of callback handlers
        **kwargs: Additional arguments to pass to the ChatOpenAI constructor

    Low Temperature (0.0 - 0.3): Good for tasks needing precision, like factual question answering or code generation.
    Medium Temperature (0.4 - 0.7): Useful for conversational or general-purpose tasks.
    High Temperature (0.8 - 1.0+): Best for creative tasks, like story writing or brainstorming.
    
    Returns:
        A ChatOpenAI instance
    """
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
        callbacks=callbacks,
        **kwargs
    ) 