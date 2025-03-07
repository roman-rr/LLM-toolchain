import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.loaders import load_text_directory
from dotenv import load_dotenv
load_dotenv()

def create_chain(directory_path="/data/raw/"):
    # Use our new loader
    splits = load_text_directory(directory_path)

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
