import os
import contextlib
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.vectorstores import create_pinecone_vectorstore, get_existing_pinecone_vectorstore
from rag.embeddings import get_openai_embeddings
from models.llms import get_openai_chat_model
from dotenv import load_dotenv
from rag.prompts.qa_prompts import get_qa_prompt
load_dotenv()

def setup_pinecone_vectors(file_path="./research.pdf", index_name="langchain-doc-embeddings", force_reload=False):
    # Load and process the PDF
    loader = PyPDFLoader(file_path)
    with open("/dev/null", "w") as f, contextlib.redirect_stderr(f):
        docs = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    embedding_model = get_openai_embeddings()

    # Use our centralized module to create or get the vectorstore
    if not force_reload:
        try:
            # Try to get existing vectorstore first
            return get_existing_pinecone_vectorstore(index_name=index_name, embedding_model=embedding_model)
        except Exception as e:
            print(f"Error getting existing index: {str(e)}. Creating new index.")
            
    # Create new vectorstore with documents
    return create_pinecone_vectorstore(
        documents=splits,
        index_name=index_name,
        embedding_model=embedding_model,
        force_reload=force_reload
    )

def create_chain_from_vectorstore(vectorstore):
    # Initialize LLM with a moderate temperature using our centralized module
    llm = get_openai_chat_model(model_name="gpt-4", temperature=0.4)
    
    # Create retriever
    retriever = vectorstore.as_retriever()

    # Create prompt template
    prompt = get_qa_prompt()

    # Create and return the chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

def create_chain(index_name="langchain-doc-embeddings", file_path="./research.pdf", force_reload=False):
    vectorstore = setup_pinecone_vectors(
        file_path=file_path,
        index_name=index_name,
        force_reload=force_reload
    )
    return create_chain_from_vectorstore(vectorstore)