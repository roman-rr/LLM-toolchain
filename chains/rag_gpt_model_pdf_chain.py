import getpass
import os
import sys
import contextlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.loaders import load_pdf
from rag.vectorstores import create_in_memory_vectorstore
from rag.embeddings import get_openai_embeddings
from models.llms import get_openai_chat_model
from dotenv import load_dotenv
from rag.prompts.qa_prompts import get_qa_prompt
load_dotenv()

def create_chain(file_path="/data/raw/research.pdf"):
    # Use our new loader
    splits = load_pdf(file_path)
    
    embedding_model = get_openai_embeddings()
    
    # Create vector store using our centralized module
    vectorstore = create_in_memory_vectorstore(documents=splits, embedding_model=embedding_model)
    
    retriever = vectorstore.as_retriever()

    # Use the centralized prompt
    prompt = get_qa_prompt()

    # Use our centralized LLM module
    llm = get_openai_chat_model(model_name="gpt-4", temperature=0.4)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)