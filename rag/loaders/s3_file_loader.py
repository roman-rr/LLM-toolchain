# https://python.langchain.com/api_reference/_modules/langchain_community/document_loaders/s3_file.html#S3FileLoader

import os
from typing import List, Optional, Dict, Any, Union, Callable

from langchain_community.document_loaders import S3FileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_s3_file(
    bucket_name: str,
    file_key: str,
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
    boto_config: Optional[Any] = None,
    mode: str = "single",
    post_processors: Optional[List[Callable]] = None,
    **unstructured_kwargs: Any
) -> List[Document]:
    """
    Load and split a file from AWS S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        file_key: Key of the file in the bucket
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
        mode: Mode in which to read the file. Valid options are: single, paged and elements
        post_processors: Post processing functions to be applied to extracted elements
        **unstructured_kwargs: Arbitrary additional kwargs to pass to unstructured's partition function
        
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
    
    # Add unstructured-specific parameters
    unstructured_params = {}
    if mode:
        unstructured_params["mode"] = mode
    if post_processors:
        unstructured_params["post_processors"] = post_processors
    if unstructured_kwargs:
        unstructured_params.update(unstructured_kwargs)
    
    # Load the file from S3
    loader = S3FileLoader(
        bucket=bucket_name, 
        key=file_key, 
        **aws_credentials,
        **unstructured_params
    )
    docs = loader.load()
    
    # Split the documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(docs) 