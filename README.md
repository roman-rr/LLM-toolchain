<p align="left">
     <img alt="A tool that helps you stay focused longer and boost your work productivity" src="/LLM-toolchain.jpg" width="500" />
</p>


# LLM Toolchain based on LangChain

A comprehensive toolchain for Large Language Models (LLMs) built on LangChain, providing a flexible framework for document processing, retrieval-augmented generation (RAG), structured data retrieval (SDR) and model evaluation.

## Key Capabilities

- **LangChain Integration**: Leverages LangChain's powerful components for building sophisticated LLM applications
- **RAG (Retrieval Augmented Generation)**: Multiple implementations for enhanced context-aware responses
- **SDR (Structured Data Retrieval)**: Querying structured data stored in relational databases (e.g., PostgreSQL, MySQL, SQLite).
- **Fine Tuning Models**: Support for custom model fine-tuning and specialized chain creation
- **Vector Database** Support Pinecone and other intergations
- **Experiments**: Integrated experiment tracking and evaluation using LangSmith
- **Evaluations**: Comprehensive evaluation framework for assessing model performance

## Useful docs
- Dashboard – https://smith.langchain.com/
- Models – https://python.langchain.com/docs/integrations/chat/
- Document loaders – https://python.langchain.com/docs/integrations/document_loaders/
- Vector Stores - https://python.langchain.com/docs/integrations/vectorstores/
- Retrievers – https://python.langchain.com/docs/integrations/retrievers/
- Tutorials - https://python.langchain.com/docs/tutorials/

## Usage
### Quick Installation
- `cd LLM-toolchain`
- `cp .env-example .env`
- `python3.12 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

### Run any chain from terminal
- `python -m chains.rag_gpt_model_s3_chain`

## API
Application serverd at AWS python-functions

### Usage
- `arc sandbox`

### Deploy
Using architect arc.codes
- `arc deploy`
- `arc deploy production`

