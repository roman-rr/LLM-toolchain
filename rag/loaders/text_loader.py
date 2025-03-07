import os
from typing import List, Optional

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_text_directory(
    directory_path: str,
    glob_pattern: str = "**/*.txt",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    encoding: str = "utf-8",
    show_progress: bool = True,
    use_multithreading: bool = True
) -> List[Document]:
    """
    Load and split text files from a directory.
    
    Args:
        directory_path: Path to the directory containing text files
        glob_pattern: Pattern to match files (default: all .txt files recursively)
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        encoding: Text encoding
        show_progress: Whether to show progress bar
        use_multithreading: Whether to use multithreading for loading
        
    Returns:
        List of document chunks
    """
    # Check if directory exists
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Load all text files from the directory
    loader = DirectoryLoader(
        directory_path,
        glob=glob_pattern,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": encoding},
        show_progress=show_progress,
        use_multithreading=use_multithreading
    )
    
    docs = loader.load()
    
    # Split the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(docs)

def load_text_file(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    encoding: str = "utf-8"
) -> List[Document]:
    """
    Load and split a single text file.
    
    Args:
        file_path: Path to the text file
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        encoding: Text encoding
        
    Returns:
        List of document chunks
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    # Load the text file
    loader = TextLoader(file_path, encoding=encoding)
    docs = loader.load()
    
    # Split the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(docs) 