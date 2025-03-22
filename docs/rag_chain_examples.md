# RAG Query CLI Options

This document lists all available options for the RAG query command-line interface.

## Basic Usage

```bash
python -m cli.rag_query --source_type SOURCE_TYPE --vectorstore_type VECTOR_STORE_TYPE --query "Your question" [other options]
```

## Source Types

| Source Type | Description | Required Parameters |
|-------------|-------------|---------------------|
| `pdf` | Query a local PDF file | `--source_path` |
| `text_file` | Query a local text file | `--source_path` |
| `text_directory` | Query multiple text files from a local directory | `--source_path` |
| `s3_file` | Query a single file from an S3 bucket | `--bucket`, `--file` |
| `s3_directory` | Query multiple files from an S3 directory | `--bucket`, `--prefix` |
| `embeddings` | Use existing embeddings from vectorstore | None |

## Vector Store Types

| Vector Store Type | Description | Additional Configuration |
|-------------------|-------------|--------------------------|
| `IN_MEMORY` | In-memory vector store (default) | No additional configuration needed |
| `PINECONE` | Pinecone vector database | Requires `PINECONE_API_KEY` environment variable |

## All Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--bucket` | S3 bucket name | Required for S3 sources |
| `--file` | S3 file key (for single file) | Required for S3_FILE |
| `--prefix` | S3 prefix/directory | Required for S3_DIRECTORY |
| `--source_path` | Local file or directory path | Required for local sources |
| `--source_type` | Source type | S3_FILE |
| `--vectorstore_type` | Vector store type | IN_MEMORY |
| `--file_extension` | File extension filter (comma-separated for multiple) | .txt |
| `--query` | Question to ask about the documents | Required |
| `--aws_access_key_id` | AWS access key ID | From environment |
| `--aws_secret_access_key` | AWS secret access key | From environment |
| `--region` | AWS region name | From environment |
| `--model` | LLM model to use | gpt-4 |
| `--temperature` | Temperature setting for the LLM | 0.4 |
| `--force_reload` | Force reload the vectorstore | False |

## Examples

### Query a single PDF file from S3

```bash
python -m cli.rag_query --source_type s3_file --bucket carftflow-demo --file rag-documents/research.pdf --query "What are the key findings?"
```

### Query all text files in an S3 directory

```bash
python -m cli.rag_query --source_type s3_directory --bucket carftflow-demo --prefix rag-documents/ --file_extension .txt --query "Summarize these reports"
```

### Query all files in an S3 directory regardless of extension

```bash
python -m cli.rag_query --source_type s3_directory --bucket carftflow-demo --prefix rag-documents/ --file_extension all --query "What insights can you find?"
```

### Query a local PDF file

```bash
python -m cli.rag_query --source_type pdf --source_path ./data/raw/research.pdf --query "Explain the main concept"
```

### Query local text files with custom model and temperature

```bash
python -m cli.rag_query --source_type text_directory --source_path ./data/raw --file_extension .txt,.md --model gpt-3.5-turbo --temperature 0.7 --query "Analyze these documents"
```

### Using different vector stores

```bash
# Using in-memory vector store (default)
python -m cli.rag_query --vectorstore_type in_memory --source_type text_file --source_path ./data/raw/example.txt --query "Summarize this document"

# Using Pinecone (requires PINECONE_API_KEY environment variable)
python -m cli.rag_query --vectorstore_type pinecone --source_type pdf --source_path ./data/raw/research.pdf --query "What methodology was used?"
```

### Vector Store Management Examples

```bash
# Will try to add documents to current vector store index
python -m cli.rag_query --vectorstore_type pinecone --source_type pdf --source_path ./data/raw/research.pdf --query "What research about?" --index_name "langchain-doc-embeddings"

# Force reload the vectorstore (clears existing vectors first)
python -m cli.rag_query --vectorstore_type pinecone --source_type pdf --source_path ./data/raw/research.pdf --force_reload --query "What are the key findings?" --index_name "langchain-doc-embeddings"
```


### Using Existing Embeddings

```bash
# Query existing embeddings in Pinecone without loading new documents
python -m cli.rag_query --source_type embeddings --vectorstore_type pinecone --query "What research about?" --index_name "langchain-doc-embeddings"

# Query existing embeddings with specific index name
python -m cli.rag_query --source_type embeddings --vectorstore_type pinecone --index_name "langchain-doc-embeddings" --query "What are the key findings?"
```

Note: The `embeddings` source type is useful when you want to query existing vectors in your vectorstore without loading new documents. This is particularly useful with persistent vectorstores like Pinecone where you've previously loaded and embedded documents.