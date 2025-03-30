<p align="left">
     <img alt="A tool that helps you stay focused longer and boost your work productivity" src="/LLM-toolchain.jpg" width="500" />
</p>


# LLM Toolchain based on LangChain

A comprehensive toolchain for Large Language Models (LLMs) built on LangChain, providing a flexible framework for document processing, retrieval-augmented generation (RAG), structured data retrieval (SDR), agent orchestration, and model evaluation.

## Key Capabilities

- **LangChain Integration**: Leverages LangChain's powerful components for building sophisticated LLM applications
- **RAG (Retrieval Augmented Generation)**: Multiple implementations for enhanced context-aware responses
- **SDR (Structured Data Retrieval)**: Querying structured data stored in relational databases (e.g., PostgreSQL, MySQL, SQLite)
- **Agent Framework**: Various agent types (REACT, Conversational) with tool integration and memory
- **Tools & Actions**: Modular tools including search, calculator, weather, and custom capabilities
- **Graphs & Workflows**: Agent orchestration and complex reasoning flows using LangGraph
- **Fine Tuning Models**: Support for custom model fine-tuning and specialized chain creation
- **Vector Database**: Support for Pinecone, ChromaDB, InMemoryVectorStore and other integrations
- **Chat History**: Persistent conversation history with multithreading support
- **Experiments**: Integrated experiment tracking and evaluation using LangSmith
- **Evaluations**: Comprehensive evaluation framework for assessing model performance

## Useful docs
- Cookbook – https://github.com/langchain-ai/langsmith-cookbook/
- Dashboard – https://smith.langchain.com/
- Models – https://python.langchain.com/docs/integrations/chat/
- Document loaders – https://python.langchain.com/docs/integrations/document_loaders/
- Agent Tools – https://python.langchain.com/docs/integrations/tools/
- Vector Stores - https://python.langchain.com/docs/integrations/vectorstores/
- Retrievers – https://python.langchain.com/docs/integrations/retrievers/
- Tutorials - https://python.langchain.com/docs/tutorials/

## Usage
### Quick Installation
- `cd LLM-toolchain`
- `CAUTION: cp .env-example .env`
- `python3.12 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

### Run any chain from terminal 
[RAG Query Examples](/docs/rag_chain_examples.md)
[Chat History Examples](/docs/chat_history_chain_examples.md)
[Agent Chain Examples](/docs/agent_chain_examples.md)

## Fast API
### Dev run server
- `python -m api.main`

## Docker FAST API
### Local Run
- `docker build -t fastapi-app .`
- `docker run -p 8000:8000 --env-file .env fastapi-app`

## Terraform API deployments to ec2 example

### Create new aws ec2 infrastructure
- `cd terraform`
- `export $(cat ../.env | grep -v '^#' | xargs)`
- `set -a; source ../.env; set +a`
- `terraform init`
- `terraform plan`
- `terraform apply`
- `./deploy.sh`

### Update instance and redeploy
- `terraform taint aws_instance.app`
- `./deploy.sh`