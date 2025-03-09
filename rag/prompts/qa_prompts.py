"""
Standard prompt templates for question-answering tasks.
"""

from langchain_core.prompts import ChatPromptTemplate

# Basic QA prompt for RAG
QA_SYSTEM_PROMPT = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

# Create a reusable prompt template
def get_qa_prompt():
    """Returns the standard QA prompt template."""
    return ChatPromptTemplate.from_messages([
        ("system", QA_SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

# Specialized prompts for different use cases
DETAILED_QA_SYSTEM_PROMPT = (
    "You are an assistant for detailed question-answering tasks. "
    "Use the following pieces of retrieved context to provide a comprehensive answer "
    "to the question. If you don't know the answer, say that you don't know. "
    "Cite specific information from the context when possible."
    "\n\n"
    "{context}"
)

def get_detailed_qa_prompt():
    """Returns a more detailed QA prompt template."""
    return ChatPromptTemplate.from_messages([
        ("system", DETAILED_QA_SYSTEM_PROMPT),
        ("human", "{input}"),
    ]) 