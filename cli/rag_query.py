#!/usr/bin/env python
"""
Command-line interface for querying documents using RAG.
"""
import argparse
import os
import sys
from botocore.exceptions import NoCredentialsError, ClientError

from rag.loaders import SourceType
from rag.vectorstores import VectorStoreType
from chains.rag_chain import create_chain

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Query documents from S3 using RAG")
    parser.add_argument("--bucket", help="S3 bucket name")
    parser.add_argument("--file", help="S3 file key (for single file)")
    parser.add_argument("--prefix", help="S3 prefix/directory")
    parser.add_argument("--source_path", help="Local file or directory path")
    parser.add_argument("--source_type", type=str, choices=[t.value for t in SourceType], 
                        default=SourceType.S3_FILE.value,
                        help=f"Source type: {', '.join([t.value for t in SourceType])}")
    parser.add_argument("--vectorstore_type", type=str, choices=[t.value for t in VectorStoreType], 
                        default=VectorStoreType.IN_MEMORY.value,
                        help=f"Vector store type: {', '.join([t.value for t in VectorStoreType])}")
    parser.add_argument("--file_extension", default=".txt", 
                        help="File extension filter (for directory). Use comma-separated values for multiple extensions (e.g., '.txt,.pdf')")
    parser.add_argument("--query", required=True, help="Question to ask about the documents")
    parser.add_argument("--aws_access_key_id", help="AWS access key ID")
    parser.add_argument("--aws_secret_access_key", help="AWS secret access key")
    parser.add_argument("--region", help="AWS region name")
    parser.add_argument("--model", default="gpt-4", help="LLM model to use (default: gpt-4)")
    parser.add_argument("--temperature", type=float, default=0.4, help="Temperature setting for the LLM (default: 0.4)")
    parser.add_argument("--index_name", type=str, default="langchain-doc-embeddings",
                        help="Name of the vector store index")
    parser.add_argument("--force_reload", action="store_true",
                        help="Force reload the vectorstore")
    parser.add_argument("--namespace", type=str,
                       help="Namespace for Pinecone vectorstore")
    parser.add_argument("--collection", type=str,
                       help="Collection name for Chroma vectorstore")
    parser.add_argument("--persist_directory", type=str, default="./faiss_indexes",
                        help="Directory to persist vector stores (for FAISS and Chroma)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments based on source type
    source_type = SourceType(args.source_type)
    vectorstore_type = VectorStoreType(args.vectorstore_type)
    
    if source_type in [SourceType.S3_FILE, SourceType.S3_DIRECTORY] and not args.bucket:
        parser.error(f"--bucket is required for source type {source_type}")
    
    if source_type == SourceType.S3_FILE and not args.file:
        parser.error("--file is required for S3_FILE source type")
    
    if source_type == SourceType.S3_DIRECTORY and not args.prefix:
        parser.error("--prefix is required for S3_DIRECTORY source type")
    
    if source_type in [SourceType.PDF, SourceType.TEXT_FILE, SourceType.TEXT_DIRECTORY] and not args.source_path:
        parser.error(f"--source_path is required for source type {source_type}")
    
    # Process file extensions (convert comma-separated string to list)
    file_extensions = None
    if args.file_extension:
        if args.file_extension.lower() == "all":
            # Special case: include all file types
            file_extensions = None
        else:
            file_extensions = [ext.strip() for ext in args.file_extension.split(",")]
    
    # Check for AWS credentials
    aws_access_key_id = args.aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = args.aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    region_name = args.region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("\nWARNING: AWS credentials not found!")
        print("Please provide AWS credentials using one of the following methods:")
        print("1. Set environment variables:")
        print("   export AWS_ACCESS_KEY_ID=your_access_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   export AWS_REGION=your_region (optional)")
        print("2. Use command line arguments:")
        print("   --aws_access_key_id YOUR_KEY --aws_secret_access_key YOUR_SECRET --region YOUR_REGION")
        print("3. Configure AWS CLI:")
        print("   aws configure")
        print("\nExiting...")
        sys.exit(1)
    
    try:
        # Create the chain with appropriate parameters based on source type
        chain_kwargs = {
            "source_type": source_type,
            "vectorstore_type": vectorstore_type,
            "model_name": args.model,
            "temperature": args.temperature,
            "force_reload": args.force_reload,
            "namespace": args.namespace,
            "collection_name": args.collection,
            "persist_directory": args.persist_directory,
        }
        
        # Add source-specific parameters
        if source_type in [SourceType.PDF, SourceType.TEXT_FILE, SourceType.TEXT_DIRECTORY]:
            print(f"Loading from {args.source_path}...")
            chain_kwargs["source_path"] = args.source_path
            
        elif source_type == SourceType.S3_FILE:
            print(f"Loading file {args.file} from bucket {args.bucket}...")
            chain_kwargs.update({
                "bucket_name": args.bucket,
                "file_key": args.file,
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "region_name": region_name
            })
            
        elif source_type == SourceType.S3_DIRECTORY:
            if file_extensions:
                print(f"Loading files with prefix {args.prefix} and extensions {', '.join(file_extensions)} from bucket {args.bucket}...")
            else:
                print(f"Loading all files with prefix {args.prefix} from bucket {args.bucket}...")
                
            chain_kwargs.update({
                "bucket_name": args.bucket,
                "prefix": args.prefix,
                "file_extension": file_extensions,
                "aws_access_key_id": aws_access_key_id,
                "aws_secret_access_key": aws_secret_access_key,
                "region_name": region_name
            })
        
        # Create the chain with the appropriate parameters
        chain = create_chain(**chain_kwargs)
        
        # Invoke the chain
        print(f"\nQuestion: {args.query}")
        print("\nProcessing...")
        
        response = chain.invoke({"input": args.query})
        
        # Print the answer
        print("\nAnswer:")
        print(response["answer"])
        
        # Print context documents if available
        if "context" in response:
            print("\nContext Documents:")
            for i, doc in enumerate(response["context"]):
                print(f"\nDocument {i+1}:")
                print(f"Content: {doc.page_content[:200]}...")  # Print first 200 chars
                print(f"Metadata: {doc.metadata}")
                
    except NoCredentialsError:
        print("\nERROR: AWS credentials not found or are invalid.")
        print("Please check your AWS credentials and try again.")
        sys.exit(1)
    except ClientError as e:
        print(f"\nERROR: AWS API error: {e}")
        print("Please check your AWS credentials, region, and bucket name.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 