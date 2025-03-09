from enum import Enum
from typing import List, Optional, Union, Any, Callable

from langchain_core.documents import Document

from .pdf_loader import load_pdf
from .text_loader import load_text_directory, load_text_file
from .s3_file_loader import load_s3_file
from .s3_directory_loader import load_s3_directory


class SourceType(str, Enum):
    """Enum for different types of data sources"""
    PDF = "pdf"
    TEXT_DIRECTORY = "text_directory"
    TEXT_FILE = "text_file"
    S3_FILE = "s3_file"
    S3_DIRECTORY = "s3_directory"


def get_loader(
    source_type: SourceType,
    source_path: str = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    # S3 specific parameters
    bucket_name: str = None,
    file_key: str = None,
    prefix: str = None,
    file_extension: Optional[Union[str, List[str]]] = None,
    # AWS credentials
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    region_name: Optional[str] = None,
    # Additional parameters
    encoding: str = "utf-8",
    show_progress: bool = True,
    use_multithreading: bool = True,
    glob_pattern: str = "**/*.txt",
    silent: bool = True,
    # S3 file loader specific parameters
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
    Get document loader based on source type and parameters.
    
    Args:
        source_type: Type of source data
        source_path: Path to the source (for local files/directories)
        chunk_size: Size of each text chunk
        chunk_overlap: Overlap between chunks
        
        # S3 specific parameters
        bucket_name: Name of the S3 bucket
        file_key: Key of the file in the bucket
        prefix: Prefix (folder path) in the bucket
        file_extension: Optional file extension(s) to filter by
        
        # AWS credentials
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        aws_session_token: AWS session token
        region_name: AWS region name
        
        # Additional parameters
        encoding: Text encoding for text files
        show_progress: Whether to show progress bar
        use_multithreading: Whether to use multithreading for loading
        glob_pattern: Pattern to match files
        silent: Whether to suppress stderr output for PDF loading
        
        # S3 file loader specific parameters
        endpoint_url: Custom endpoint URL
        use_ssl: Whether to use SSL
        verify: Whether to verify SSL certificates
        api_version: AWS API version
        boto_config: Advanced boto3 client configuration
        mode: Mode in which to read the file (for S3 file loader)
        post_processors: Post processing functions (for S3 file loader)
        **unstructured_kwargs: Additional kwargs for unstructured library
        
    Returns:
        List of document chunks
    """
    if source_type == SourceType.PDF:
        if not source_path:
            raise ValueError("source_path is required for PDF loader")
        return load_pdf(
            file_path=source_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            silent=silent
        )
    
    elif source_type == SourceType.TEXT_DIRECTORY:
        if not source_path:
            raise ValueError("source_path is required for text directory loader")
        return load_text_directory(
            directory_path=source_path,
            glob_pattern=glob_pattern,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            encoding=encoding,
            show_progress=show_progress,
            use_multithreading=use_multithreading
        )
    
    elif source_type == SourceType.TEXT_FILE:
        if not source_path:
            raise ValueError("source_path is required for text file loader")
        return load_text_file(
            file_path=source_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            encoding=encoding
        )
    
    elif source_type == SourceType.S3_FILE:
        if not bucket_name or not file_key:
            raise ValueError("bucket_name and file_key are required for S3 file loader")
        return load_s3_file(
            bucket_name=bucket_name,
            file_key=file_key,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            endpoint_url=endpoint_url,
            use_ssl=use_ssl,
            verify=verify,
            api_version=api_version,
            boto_config=boto_config,
            mode=mode,
            post_processors=post_processors,
            **unstructured_kwargs
        )
    
    elif source_type == SourceType.S3_DIRECTORY:
        if not bucket_name:
            raise ValueError("bucket_name is required for S3 directory loader")
        return load_s3_directory(
            bucket_name=bucket_name,
            prefix=prefix or "",
            file_extension=file_extension,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            endpoint_url=endpoint_url,
            use_ssl=use_ssl,
            verify=verify,
            api_version=api_version,
            boto_config=boto_config
        )
    
    else:
        raise ValueError(f"Unsupported source type: {source_type}") 