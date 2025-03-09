# RAG Query CLI Options

This document lists all available options for the RAG query command-line interface.

## Basic Usage

```bash
python -m cli.rag_query --source_type SOURCE_TYPE --vectorstore_type VECTOR_STORE_TYPE --query "Your question" [other options]
```

## Source Types

| Source Type | Description | Required Parameters |
|-------------|-------------|---------------------|
| `S3_FILE` | Query a single file from an S3 bucket | `--bucket`, `--file` |
| `S3_DIRECTORY` | Query multiple files from an S3 directory | `--bucket`, `--prefix` |
| `PDF` | Query a local PDF file | `--source_path` |
| `TEXT_FILE` | Query a local text file | `--source_path` |
| `TEXT_DIRECTORY` | Query multiple text files from a local directory | `--source_path` |

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

## Examples

### Query a single PDF file from S3

```bash
python -m cli.rag_query --bucket research-docs --file papers/research.pdf --query "What are the key findings?"
```

### Query all text files in an S3 directory

```bash
python -m cli.rag_query --source_type S3_DIRECTORY --bucket my-docs --prefix reports/ --file_extension .txt --query "Summarize these reports"
```

### Query all files in an S3 directory regardless of extension

```bash
python -m cli.rag_query --source_type S3_DIRECTORY --bucket my-docs --prefix data/ --file_extension all --query "What insights can you find?"
```

### Query a local PDF file

```bash
python -m cli.rag_query --source_type PDF --source_path ./document.pdf --query "Explain the main concept"
```

### Query local text files with custom model and temperature

```bash
python -m cli.rag_query --source_type TEXT_DIRECTORY --source_path ./documents --file_extension .txt,.md --model gpt-3.5-turbo --temperature 0.7 --query "Analyze these documents"
```

### Using different vector stores

```bash
# Using in-memory vector store (default)
python -m cli.rag_query --vectorstore_type IN_MEMORY --source_type TEXT_FILE --source_path ./document.txt --query "Summarize this document"

# Using Pinecone (requires PINECONE_API_KEY environment variable)
python -m cli.rag_query --vectorstore_type PINECONE --source_type PDF --source_path ./research.pdf --query "What methodology was used?"
```