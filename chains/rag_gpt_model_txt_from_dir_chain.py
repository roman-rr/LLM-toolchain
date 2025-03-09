import os
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from rag.loaders import load_text_directory
from rag.vectorstores import create_in_memory_vectorstore
from rag.embeddings import get_openai_embeddings
from models.llms import get_openai_chat_model
from rag.prompts.qa_prompts import get_qa_prompt
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
    prompt = get_qa_prompt()

    # Create the question-answering chain using our centralized LLM module
    llm = get_openai_chat_model(model_name="gpt-4")
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)
