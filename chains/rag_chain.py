import os
from typing import List, Optional, Union, Any, Callable
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from enum import Enum

from rag.loaders import get_loader, SourceType
from rag.vectorstores import get_vectorstore, VectorStoreType
from models.llms import get_openai_chat_model
from rag.embeddings import get_openai_embeddings
from rag.prompts.qa_prompts import get_qa_prompt

from dotenv import load_dotenv
load_dotenv()

def create_chain(
    source_type: SourceType = None,
    source_path: str = None,
    bucket_name: str = None, 
    file_key: str = None, 
    prefix: str = None,
    index_name: str = "langchain-doc-embeddings",
    vectorstore_type: VectorStoreType = VectorStoreType.IN_MEMORY,
    force_reload: bool = False,
    chroma_db_path: str = "./chroma_db",
    model_name: str = "gpt-4",
    temperature: float = 0.4,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    similarity_threshold: float = 0.7,
    max_documents: int = 6,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_session_token: str = None,
    region_name: str = None,
    file_extension: Union[str, List[str]] = ".txt",
    # Additional parameters for specific loaders
    encoding: str = "utf-8",
    show_progress: bool = True,
    use_multithreading: bool = True,
    glob_pattern: str = "**/*.txt",
    silent: bool = True,
    endpoint_url: Optional[str] = None,
    use_ssl: Optional[bool] = True,
    verify: Union[str, bool, None] = None,
    api_version: Optional[str] = None,
    boto_config: Optional[Any] = None,
    mode: str = "single",
    post_processors: Optional[List[Callable]] = None,
    **unstructured_kwargs
):
    """
    Create a RAG chain that can process various types of data sources.
    
    Args:
        source_type: Type of source data (PDF, TEXT_DIRECTORY, S3_FILE, etc.)
        source_path: Path to the source (for local files/directories)
        bucket_name: S3 bucket name (for S3 sources)
        file_key: S3 file key (for single S3 file)
        prefix: S3 prefix/directory (for S3 directory)
        index_name: Name of the index (for Pinecone)
        vectorstore_type: Type of vectorstore to use
        chroma_db_path: Path to store Chroma database files (default: ./chroma_db)
        force_reload: Whether to force reload the index with new documents
        model_name: Name of the LLM model to use
        temperature: Temperature setting for the LLM
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        similarity_threshold: Minimum similarity score (0-1) for retrieved documents
        max_documents: Maximum number of documents to retrieve
        aws_access_key_id: AWS access key ID (for S3 sources)
        aws_secret_access_key: AWS secret access key (for S3 sources)
        aws_session_token: AWS session token (for S3 sources)
        region_name: AWS region name (for S3 sources)
        file_extension: File extension filter (for directory sources)
        
        # Additional parameters for specific loaders
        encoding: Text encoding for text files
        show_progress: Whether to show progress bar
        use_multithreading: Whether to use multithreading for loading
        glob_pattern: Pattern to match files
        silent: Whether to suppress stderr output for PDF loading
        endpoint_url: Custom endpoint URL for S3
        use_ssl: Whether to use SSL for S3
        verify: Whether to verify SSL certificates for S3
        api_version: AWS API version for S3
        boto_config: Advanced boto3 client configuration for S3
        mode: Mode in which to read the file (for S3 file loader)
        post_processors: Post processing functions (for S3 file loader)
        **unstructured_kwargs: Additional kwargs for unstructured library
        
    Returns:
        A retrieval chain
    """
    # Handle backward compatibility for S3 sources
    if bucket_name and (file_key or prefix) and not source_type:
        if file_key:
            source_type = SourceType.S3_FILE
        elif prefix:
            source_type = SourceType.S3_DIRECTORY
    
    # Validate required parameters
    if not source_type:
        raise ValueError("Either source_type or bucket_name with file_key/prefix must be provided")
    
    # Prepare kwargs for the loader based on source type
    kwargs = {
        "source_type": source_type,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap
    }
    
    # Add source-specific parameters
    if source_type in [SourceType.PDF, SourceType.TEXT_FILE, SourceType.TEXT_DIRECTORY]:
        if not source_path:
            raise ValueError(f"source_path is required for {source_type}")
        kwargs["source_path"] = source_path
        
        # Add text-specific parameters
        if source_type in [SourceType.TEXT_FILE, SourceType.TEXT_DIRECTORY]:
            kwargs["encoding"] = encoding
            
        if source_type == SourceType.TEXT_DIRECTORY:
            kwargs["glob_pattern"] = glob_pattern
            kwargs["show_progress"] = show_progress
            kwargs["use_multithreading"] = use_multithreading
            
        if source_type == SourceType.PDF:
            kwargs["silent"] = silent
            
    elif source_type == SourceType.S3_FILE:
        if not bucket_name or not file_key:
            raise ValueError("bucket_name and file_key are required for S3_FILE")
        kwargs["bucket_name"] = bucket_name
        kwargs["file_key"] = file_key
        kwargs["aws_access_key_id"] = aws_access_key_id
        kwargs["aws_secret_access_key"] = aws_secret_access_key
        kwargs["aws_session_token"] = aws_session_token
        kwargs["region_name"] = region_name
        kwargs["endpoint_url"] = endpoint_url
        kwargs["use_ssl"] = use_ssl
        kwargs["verify"] = verify
        kwargs["api_version"] = api_version
        kwargs["boto_config"] = boto_config
        kwargs["mode"] = mode
        kwargs["post_processors"] = post_processors
        kwargs.update(unstructured_kwargs)
        
    elif source_type == SourceType.S3_DIRECTORY:
        if not bucket_name:
            raise ValueError("bucket_name is required for S3_DIRECTORY")
        kwargs["bucket_name"] = bucket_name
        kwargs["prefix"] = prefix or ""
        kwargs["file_extension"] = file_extension
        kwargs["aws_access_key_id"] = aws_access_key_id
        kwargs["aws_secret_access_key"] = aws_secret_access_key
        kwargs["aws_session_token"] = aws_session_token
        kwargs["region_name"] = region_name
        kwargs["endpoint_url"] = endpoint_url
        kwargs["use_ssl"] = use_ssl
        kwargs["verify"] = verify
        kwargs["api_version"] = api_version
        kwargs["boto_config"] = boto_config
    
    # Load documents using the unified loader interface
    splits = get_loader(**kwargs)
    
    # Validate that we have documents to process
    if not splits or (isinstance(splits, list) and len(splits) == 0):
        raise ValueError("No documents were loaded. Please check your source path and make sure the file exists and is not empty.")
    
    if isinstance(splits, list):
        print(f"Loaded {len(splits)} document splits")
    
    # Get embedding model
    embedding_model = get_openai_embeddings()

    try:
        # Create vector store
        vectorstore = get_vectorstore(
            documents=splits, 
            vectorstore_type=vectorstore_type,
            embedding_model=embedding_model,
            index_name=index_name,
            force_reload=force_reload
        )

        print("Vectorstore created with type: ", vectorstore_type)
        
        # Create retriever with vectorstore-specific configurations
        if vectorstore_type == VectorStoreType.CHROMA:
            retriever = vectorstore.as_retriever(
                search_type="mmr",  # Use MMR for Chroma to ensure diversity
                search_kwargs={
                    "k": max_documents,
                    "fetch_k": max_documents * 3,  # Fetch more candidates for MMR
                    "lambda_mult": 0.7  # Diversity vs relevance trade-off
                }
            )
        elif vectorstore_type == VectorStoreType.PINECONE:
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": max_documents,
                    "score_threshold": similarity_threshold
                }
            )
        else:  # IN_MEMORY and others
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": max_documents
                }
            )
        
        # Define prompt template
        prompt = get_qa_prompt()

        # Create the chain
        llm = get_openai_chat_model(model_name=model_name, temperature=temperature)
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever, question_answer_chain)
    except Exception as e:
        raise Exception(f"Error creating RAG chain: {str(e)}")