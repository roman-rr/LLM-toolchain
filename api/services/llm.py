from typing import Tuple, List, Dict, Any, Optional
from rag.loaders import SourceType
from rag.vectorstores import VectorStoreType
from chains.rag_chain import create_chain
from api.services.s3 import S3Service

class LLMService:
    def __init__(self):
        self.s3_service = S3Service()
        
    async def process_rag_query(
        self,
        query: str,
        context_files: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a RAG query using specified context files from S3.
        
        Args:
            query: The user's query
            context_files: Optional list of specific file IDs/paths to use as context
            options: Additional options for processing
            temperature: Temperature setting for the LLM
            
        Returns:
            Tuple containing (answer, context_documents)
        """
        options = options or {}
        
        # Set up default options
        bucket_name = options.get("bucket_name", "carftflow-demo")
        prefix = options.get("prefix", "uploads/")
        model_name = options.get("model_name", "gpt-4")
        file_extensions = options.get("file_extensions", [".txt", ".pdf", ".doc"])
        
        # If specific files are provided, adjust the prefix to target those files
        if context_files:
            # Verify files exist in S3
            for file_path in context_files:
                if not await self.s3_service.file_exists(bucket_name, file_path):
                    raise ValueError(f"File not found in S3: {file_path}")
            
            # Use the directory containing the specified files
            if len(context_files) > 0:
                # Get the common prefix from the specified files
                prefix = self._get_common_prefix(context_files)
        
        try:
            # Create and invoke the RAG chain
            chain = create_chain(
                source_type=SourceType.S3_DIRECTORY,
                vectorstore_type=VectorStoreType.IN_MEMORY,
                bucket_name=bucket_name,
                prefix=prefix,
                file_extension=file_extensions,
                model_name=model_name,
                temperature=temperature,
                # Add any additional options from the request
                **options.get("chain_options", {})
            )
            
            # Process the query
            response = chain.invoke({"input": query})
            
            # Format context documents
            context_docs = []
            if "context" in response:
                for doc in response["context"]:
                    context_docs.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "unknown")
                    })
            
            return response["answer"], context_docs
            
        except Exception as e:
            raise Exception(f"Error processing RAG query: {str(e)}")
    
    def _get_common_prefix(self, file_paths: List[str]) -> str:
        """
        Get the common prefix from a list of file paths.
        """
        if not file_paths:
            return ""
        
        # Split all paths into components
        split_paths = [path.split('/') for path in file_paths]
        
        # Find the common prefix
        common_prefix = []
        for i in range(len(min(split_paths, key=len))):
            if len(set(path[i] for path in split_paths)) == 1:
                common_prefix.append(split_paths[0][i])
            else:
                break
        
        return '/'.join(common_prefix) + '/' if common_prefix else ""
