# https://python.langchain.com/api_reference/_modules/langchain_community/document_loaders/s3_directory.html#S3DirectoryLoader

import os
from typing import List, Optional, Dict, Any, Union

from langchain_community.document_loaders import S3DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_s3_directory(
    bucket_name: str,
    prefix: str = "",
    file_extension: Optional[Union[str, List[str]]] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    region_name: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    use_ssl: Optional[bool] = True,
    verify: Union[str, bool, None] = None,
    api_version: Optional[str] = None,
    boto_config: Optional[Any] = None
) -> List[Document]:
    """
    Load and split files from a directory in AWS S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        prefix: Prefix (folder path) in the bucket
        file_extension: Optional file extension(s) to filter by. Can be a string (e.g., ".txt") 
                       or a list of strings (e.g., [".txt", ".pdf"]). Pass None to include all files.
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        aws_access_key_id: AWS access key ID (optional, can use env vars)
        aws_secret_access_key: AWS secret access key (optional, can use env vars)
        aws_session_token: AWS session token (optional)
        region_name: AWS region name (optional)
        endpoint_url: Custom endpoint URL (optional)
        use_ssl: Whether to use SSL (default: True)
        verify: Whether to verify SSL certificates (default: None)
        api_version: AWS API version (optional)
        boto_config: Advanced boto3 client configuration (optional)
        
    Returns:
        List of document chunks
    """
    # Prepare AWS credentials and config
    aws_credentials = {}
    if aws_access_key_id:
        aws_credentials["aws_access_key_id"] = aws_access_key_id
    if aws_secret_access_key:
        aws_credentials["aws_secret_access_key"] = aws_secret_access_key
    if aws_session_token:
        aws_credentials["aws_session_token"] = aws_session_token
    if region_name:
        aws_credentials["region_name"] = region_name
    if endpoint_url:
        aws_credentials["endpoint_url"] = endpoint_url
    if use_ssl is not None:
        aws_credentials["use_ssl"] = use_ssl
    if verify is not None:
        aws_credentials["verify"] = verify
    if api_version:
        aws_credentials["api_version"] = api_version
    if boto_config:
        aws_credentials["boto_config"] = boto_config
    
    # Load files from S3 directory
    loader = S3DirectoryLoader(
        bucket=bucket_name,
        prefix=prefix,
        **aws_credentials
    )
    
    docs = loader.load()
    
    # Filter by file extension if specified
    if file_extension:
        # Convert single extension to list for consistent handling
        if isinstance(file_extension, str):
            extensions = [file_extension]
        else:
            extensions = file_extension
            
        # Filter documents that end with any of the specified extensions
        filtered_docs = []
        for doc in docs:
            source = doc.metadata.get("source", "")
            if any(source.endswith(ext) for ext in extensions):
                filtered_docs.append(doc)
        docs = filtered_docs
    
    # Split the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(docs) 