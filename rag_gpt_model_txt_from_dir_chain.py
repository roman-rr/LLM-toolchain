import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

def create_chain(directory_path="./rag_docs/"):
    # Load all text files from the directory
    loader = DirectoryLoader(
        directory_path,
        glob="**/*.txt",  # Load all .txt files recursively
        show_progress=True,
        use_multithreading=True
    )
    docs = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    # Create vector store
    vectorstore = InMemoryVectorStore.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings()
    )

    # Create a retriever
    retriever = vectorstore.as_retriever()

    # Define the prompt template
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

    # Create the question-answering chain
    # Low Temperature (0.0 - 0.3): Good for tasks needing precision, like factual question answering or code generation.
    # Medium Temperature (0.4 - 0.7): Useful for conversational or general-purpose tasks.
    # High Temperature (0.8 - 1.0+): Best for creative tasks, like story writing or brainstorming.
    llm = ChatOpenAI(model="gpt-4")
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)
