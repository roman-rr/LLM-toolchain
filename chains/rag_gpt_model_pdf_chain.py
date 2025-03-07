import getpass
import os
import sys
import contextlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from rag.loaders import load_pdf
from dotenv import load_dotenv
load_dotenv()

def create_chain(file_path="/data/raw/research.pdf"):
    # Use our new loader
    splits = load_pdf(file_path)
    
    vectorstore = InMemoryVectorStore.from_documents(
        documents=splits, embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever()

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

    # Low Temperature (0.0 - 0.3): Good for tasks needing precision, like factual question answering or code generation.
    # Medium Temperature (0.4 - 0.7): Useful for conversational or general-purpose tasks.
    # High Temperature (0.8 - 1.0+): Best for creative tasks, like story writing or brainstorming.
    llm = ChatOpenAI(model="gpt-4", temperature=0.4)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)