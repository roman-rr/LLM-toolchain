import os
import contextlib
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_pdf(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    silent: bool = True
) -> List[Document]:
    """
    Load and split a PDF document into chunks.
    
    Args:
        file_path: Path to the PDF file
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        silent: Whether to suppress stderr output
        
    Returns:
        List of document chunks
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    # Load the PDF
    loader = PyPDFLoader(file_path)
    
    # Suppress stderr output if silent is True
    if silent:
        with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
            docs = loader.load()
    else:
        docs = loader.load()
    
    # Split the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(docs) 