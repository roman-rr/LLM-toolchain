import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.loaders.s3_file_loader import load_s3_file
from rag.loaders.s3_directory_loader import load_s3_directory

from dotenv import load_dotenv
load_dotenv()

def create_chain_from_s3_file(
    bucket_name: str,
    file_key: str,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = None
):
    """Create a RAG chain from a single S3 file"""
    # Use environment variables if credentials not provided
    aws_access_key_id = aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    region_name = region_name or os.environ.get("AWS_REGION")
    
    # Load document from S3
    splits = load_s3_file(
        bucket_name=bucket_name,
        file_key=file_key,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    # Create vector store
    vectorstore = InMemoryVectorStore.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings()
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever()
    
    # Define prompt template
    system_prompt = """
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, say that you don't know.
    Use three sentences maximum and keep the answer concise.

    Context: {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Create the chain
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

def create_chain_from_s3_directory(
    bucket_name: str,
    prefix: str = "",
    file_extension: str = ".txt",
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    region_name: str = None
):
    """Create a RAG chain from a directory of files in S3"""
    # Use environment variables if credentials not provided
    aws_access_key_id = aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
    
    # Load documents from S3 directory
    splits = load_s3_directory(
        bucket_name=bucket_name,
        prefix=prefix,
        file_extension=file_extension,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    print(f"Loaded {len(splits)} documents")

    # Create vector store
    vectorstore = InMemoryVectorStore.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings()
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever()
    
    # Define prompt template
    system_prompt = """
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, say that you don't know.
    Use three sentences maximum and keep the answer concise.

    Context: {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Create the chain
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

# Default function to maintain compatibility with existing code
def create_chain(bucket_name: str, file_key: str = None, prefix: str = None):
    """
    Create a RAG chain from S3 content.
    If file_key is provided, loads a single file.
    If prefix is provided, loads all files from that directory.
    """
    if file_key:
        return create_chain_from_s3_file(bucket_name, file_key)
    elif prefix:
        return create_chain_from_s3_directory(bucket_name, prefix)
    else:
        raise ValueError("Either file_key or prefix must be provided")

# Example usage from terminal (by file / by directorys)
# python -m chains.rag_gpt_model_s3_chain --bucket bucket-name --file rag-documents/research.pdf --query "What is the main idea of the research paper?"
# python -m chains.rag_gpt_model_s3_chain --bucket bucket-name --prefix rag-documents/ --file_extension .txt --query "Summarize the key points"
# python -m chains.rag_gpt_model_s3_chain --bucket bucket-name --prefix rag-documents/ --file_extension all --query "What is your names?"

if __name__ == "__main__":
    import argparse
    import os
    import sys
    from botocore.exceptions import NoCredentialsError, ClientError
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Query documents from S3 using RAG")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--file", help="S3 file key (for single file)")
    parser.add_argument("--prefix", help="S3 prefix/directory")
    parser.add_argument("--file_extension", default=".txt", 
                        help="File extension filter (for directory). Use comma-separated values for multiple extensions (e.g., '.txt,.pdf')")
    parser.add_argument("--query", required=True, help="Question to ask about the documents")
    parser.add_argument("--aws_access_key_id", help="AWS access key ID")
    parser.add_argument("--aws_secret_access_key", help="AWS secret access key")
    parser.add_argument("--region", help="AWS region name")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.prefix:
        parser.error("Either --file or --prefix must be provided")
    
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
        # Create the appropriate chain
        if args.file:
            print(f"Loading file {args.file} from bucket {args.bucket}...")
            chain = create_chain_from_s3_file(
                args.bucket, 
                args.file,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            if file_extensions:
                print(f"Loading files with prefix {args.prefix} and extensions {', '.join(file_extensions)} from bucket {args.bucket}...")
            else:
                print(f"Loading all files with prefix {args.prefix} from bucket {args.bucket}...")
                
            chain = create_chain_from_s3_directory(
                args.bucket, 
                args.prefix, 
                file_extensions,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        
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