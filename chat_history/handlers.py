from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

def get_streaming_llm(llm):
    """Create a streaming-enabled version of an LLM."""
    return llm.with_config({"callbacks": [StreamingStdOutCallbackHandler()]}) 