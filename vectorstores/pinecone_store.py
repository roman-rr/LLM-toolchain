def create_pinecone_store(
    documents,
    embedding_model,
    index_name: str = "langchain-doc-embeddings",
    namespace: str = None,
    force_reload: bool = False,
    **kwargs
):
    """Create a Pinecone vectorstore."""
    import pinecone
    from langchain.vectorstores import Pinecone

    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT')
    )

    # Create index if it doesn't exist
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embeddings dimension
            metric='cosine'
        )

    # Get the index
    index = pinecone.Index(index_name)

    # Delete existing vectors in the namespace if force_reload
    if force_reload and namespace:
        index.delete(deleteAll=True, namespace=namespace)

    # Create and return the vectorstore
    return Pinecone.from_documents(
        documents,
        embedding_model,
        index_name=index_name,
        namespace=namespace
    ) 