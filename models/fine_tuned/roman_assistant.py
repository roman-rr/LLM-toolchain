from langchain.prompts import PromptTemplate
from models.llms import get_openai_chat_model

def create_roman_assistant_chain():
    """
    Create a chain that responds as Roman, a virtual assistant.
    
    Returns:
        A runnable chain that can be invoked with an input question
    """
    # Define your prompt
    prompt_template = PromptTemplate(
        input_variables=["input"],
        template="""
            Answer the questions as if you are a virtual assistant named Roman.
            
            Q: What's your name?
            A: Roman
            
            Q: How can you help me?
            A: I am here to assist with your questions and provide helpful answers.

            Q: {input}
            A:
        """
    )

    # Get the LLM from our centralized module
    llm = get_openai_chat_model(model_name="gpt-4")
    
    # Use the pipe syntax to create the chain
    return prompt_template | llm