import os
import contextlib
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Pinecone as LangchainPinecone 

from dotenv import load_dotenv
load_dotenv()

def setup_pinecone_vectors(file_path="./research.pdf", index_name="langchain-doc-embeddings", force_reload=False):
    # Create an instance of the Pinecone class
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    # Create the Pinecone index if it doesn't exist
    if index_name not in pc.list_indexes().names():
        print(f"Creating index {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    else:
        print(f"Index {index_name} already exists")

    # Connect to the Pinecone index
    pinecone_index = pc.Index(index_name)
    
    # If force_reload is False and index exists with data, return existing vectorstore
    if not force_reload and pinecone_index.describe_index_stats().total_vector_count > 0:
        embedding_model = OpenAIEmbeddings()
        return LangchainPinecone.from_existing_index(
            index_name=index_name,
            embedding=embedding_model,
        )

    # Load and process the PDF
    loader = PyPDFLoader(file_path)
    with open("/dev/null", "w") as f, contextlib.redirect_stderr(f):
        docs = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Create embeddings and store in Pinecone
    embedding_model = OpenAIEmbeddings()
    
    # Delete existing vectors before updating
    if force_reload:
        pinecone_index.delete(delete_all=True)
    
    vectorstore = LangchainPinecone.from_existing_index(
        index_name=index_name,
        embedding=embedding_model,
        namespace=None  # Add namespace if needed
    )
    
    return vectorstore

def create_chain_from_vectorstore(vectorstore):
    # Initialize LLM with a moderate temperature
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)
    
    # Create retriever
    retriever = vectorstore.as_retriever()

    # Create prompt template
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create and return the chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)

def create_chain(index_name="langchain-doc-embeddings", file_path="./research.pdf", force_reload=False):
    vectorstore = setup_pinecone_vectors(
        file_path=file_path,
        index_name=index_name,
        force_reload=force_reload
    )
    return create_chain_from_vectorstore(vectorstore)