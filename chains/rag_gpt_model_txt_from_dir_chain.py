import os
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.loaders import load_text_directory
from rag.vectorstores import create_in_memory_vectorstore
from rag.embeddings import get_openai_embeddings
from models.llms import get_openai_chat_model
from dotenv import load_dotenv
load_dotenv()

def create_chain(directory_path="/data/raw/"):
    # Use our new loader
    splits = load_text_directory(directory_path)
    
    embedding_model = get_openai_embeddings()

    # Create vector store using our centralized module
    vectorstore = create_in_memory_vectorstore(documents=splits, embedding_model=embedding_model)

    # Create a retriever
    retriever = vectorstore.as_retriever()

    # Define the prompt template
    system_prompt = """
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, say that you don't know.
    Use three sentences maximum and keep the answer concise.

    Context: {context}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create the question-answering chain using our centralized LLM module
    llm = get_openai_chat_model(model_name="gpt-4")
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)
