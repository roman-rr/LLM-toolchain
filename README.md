<p align="left">
     <img alt="A tool that helps you stay focused longer and boost your work productivity" src="/LLM-toolchain.jpg" width="500" />
</p>


# LLM Toolchain based on LangChain

A comprehensive toolchain for Large Language Models (LLMs) built on LangChain, providing a flexible framework for document processing, retrieval-augmented generation (RAG), and model evaluation.

## Key Capabilities

- **LangChain Integration**: Leverages LangChain's powerful components for building sophisticated LLM applications
- **RAG (Retrieval Augmented Generation)**: Multiple implementations for enhanced context-aware responses
- **Fine Tuning Models**: Support for custom model fine-tuning and specialized chain creation
- **Vector Database** Support Pinecone and other intergations
- **Experiments**: Integrated experiment tracking and evaluation using LangSmith
- **Evaluations**: Comprehensive evaluation framework for assessing model performance

## TODO NEXT
- CI/DI: Dockerize 
- CI/DI: Deploy to AWS/Azure templates
- Chains: Chat history
= Chains: from langchain_core.documents import Document https://python.langchain.com/docs/tutorials/retrievers/
- Chains: over SQL data
- Agents https://python.langchain.com/docs/tutorials/agents/
- RAG: similarity threshold for fallback answer
- UI: Graphical Interface for documents uploading
- 2 more Vector DB supports
- 2 more Document loaders
- CI/DI: HELM + k8 deployments

## Components

- `rag_gpt_model_pdf_chain.py`: PDF document processing chain
- `rag_gpt_model_txt_from_dir_chain.py`: Text file processing chain
- `rag_gpt_model_pdf_pinecone_chain.py`: Pinecone-based document processing
- `test_chains.py`: Test utilities for different chain implementations
- `run_experiment.py`: Experiment runner with LangSmith integration
- `fine_tuned_chain.py`: Custom chain implementation
- `get_datasets.py`: Dataset management utilities


## Useful docs
- Dashboard – https://smith.langchain.com/
- Models – https://python.langchain.com/docs/integrations/chat/
- Document loaders – https://python.langchain.com/docs/integrations/document_loaders/
- Vector Stores - https://python.langchain.com/docs/integrations/vectorstores/
- Retrievers – https://python.langchain.com/docs/integrations/retrievers/
- Tutorials - https://python.langchain.com/docs/tutorials/

## Usage
- `cd LLM-toolchain`
- `python3 -m venv venv`
- `source myenv/bin/activate`
- `pip install -r requirements.txt`

Run any script with `python ...`
