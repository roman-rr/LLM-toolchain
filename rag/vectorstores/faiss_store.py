import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

def setup_faiss_vectorstore(
    documents: Optional[List[Document]],
    embedding_model: object,
    index_name: str = "langchain-doc-embeddings",
    persist_directory: str = "./faiss_indexes",
    force_reload: bool = False
) -> FAISS:
    """
    Create or get a FAISS vectorstore
    
    Args:
        documents: List of Document objects to store (optional when loading existing index)
        embedding_model: Embedding model to use for generating vectors
        index_name: Name of the index
        persist_directory: Directory to persist the FAISS index
        force_reload: Whether to force reload the index with new documents
    
    Returns:
        A FAISS vectorstore instance
    
    Raises:
        ValueError: If no documents provided when creating new index
        FileNotFoundError: If trying to load non-existent index
    """
    # Ensure the base directory exists
    faiss_dir = os.path.join(persist_directory, "faiss")
    os.makedirs(faiss_dir, exist_ok=True)
    
    # Construct full paths for index files
    index_path = os.path.join(faiss_dir, f"{index_name}.faiss")
    docstore_path = os.path.join(faiss_dir, f"{index_name}.pkl")
    
    # Check if index exists
    index_exists = os.path.exists(index_path) and os.path.exists(docstore_path)
    
    # Handle different scenarios
    if force_reload or not index_exists:
        if documents is None:
            raise ValueError(
                f"No documents provided to create new index '{index_name}'. "
                "Documents are required when creating a new index or force reloading."
            )
            
        print(f"Creating new FAISS index: {index_name}")
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=embedding_model,
            ids=[doc.metadata.get('doc_id') for doc in documents]
        )
        
        # Save the index
        vectorstore.save_local(faiss_dir, index_name)
        print(f"Saved index to {faiss_dir}")
        
    else:
        try:
            print(f"Loading existing FAISS index: {index_name}")
            vectorstore = FAISS.load_local(
                faiss_dir,
                embedding_model,
                index_name,
                allow_dangerous_deserialization=True # TODO: Remove this on productions
            )
            
            if documents:
                # Get existing IDs to avoid duplicates
                existing_ids = set(vectorstore.docstore._dict.keys())
                new_docs = []
                new_ids = []
                
                for doc in documents:
                    doc_id = doc.metadata.get('doc_id')
                    if doc_id not in existing_ids:
                        new_docs.append(doc)
                        new_ids.append(doc_id)
                
                if new_docs:
                    print(f"Adding {len(new_docs)} new documents to existing index")
                    vectorstore.add_documents(new_docs, ids=new_ids)
                    vectorstore.save_local(faiss_dir, index_name)
                
        except Exception as e:
            raise FileNotFoundError(
                f"Failed to load FAISS index '{index_name}' from {faiss_dir}. "
                f"Error: {str(e)}"
            )
    
    return vectorstore 