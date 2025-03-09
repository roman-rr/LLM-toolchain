import os
from enum import Enum
from typing import List, Optional, Union
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from rag.vectorstores import get_vectorstore, VectorStoreType
from rag.embeddings import get_openai_embeddings
from models.llms import get_openai_chat_model
from rag.prompts.qa_prompts import get_qa_prompt
from rag.loaders.pdf_loader import load_pdf
from rag.loaders.text_loader import load_text_directory
from dotenv import load_dotenv
load_dotenv()


class SourceType(str, Enum):
    """Enum for different types of data sources"""
    PDF = "pdf"
    TEXT_DIRECTORY = "text_directory"


def create_chain(
    source_type: SourceType = SourceType.PDF,
    source_path: str = "/data/raw/research.pdf",
    index_name: str = "langchain-doc-embeddings",
    vectorstore_type: VectorStoreType = VectorStoreType.IN_MEMORY,
    force_reload: bool = False,
    model_name: str = "gpt-4",
    temperature: float = 0.4,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Create a RAG chain that can process either PDF files or text directories.
    
    Args:
        source_type: Type of source data (PDF or TEXT_DIRECTORY)
        source_path: Path to the source (PDF file or directory)
        index_name: Name of the index (for Pinecone)
        vectorstore_type: Type of vectorstore to use
        force_reload: Whether to force reload the index with new documents
        model_name: Name of the LLM model to use
        temperature: Temperature setting for the LLM
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        A retrieval chain
    """
    # Load and split the documents based on source type
    if source_type == SourceType.PDF:
        splits = load_pdf(
            file_path=source_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    elif source_type == SourceType.TEXT_DIRECTORY:
        splits = load_text_directory(
            directory_path=source_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    else:
        raise ValueError(f"Unsupported source type: {source_type}")
    
    # Get embedding model
    embedding_model = get_openai_embeddings()

    vectorstore = get_vectorstore(
        documents=splits, 
        vectorstore_type=vectorstore_type,
        embedding_model=embedding_model,
        index_name=index_name,
        force_reload=force_reload
    )

    # Initialize LLM
    llm = get_openai_chat_model(model_name=model_name, temperature=temperature)
    
    # Create retriever
    retriever = vectorstore.as_retriever()

    # Create prompt template
    prompt = get_qa_prompt()

    # Create and return the chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain) 