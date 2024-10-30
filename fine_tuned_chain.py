from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence

def create_chain():
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

    llm = ChatOpenAI(model_name="gpt-4")
    # Use the new pipe syntax instead of LLMChain
    return prompt_template | llm

# Create and export the chain
chain = create_chain()

# Only run test if this file is run directly
if __name__ == "__main__":
    response = chain.invoke({"input": "What's your name?"})
    print(response.content)  # Use .content to get the response text
