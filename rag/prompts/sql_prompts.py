"""
Prompt templates for SQL-related tasks.
"""

from langchain_core.prompts import ChatPromptTemplate

# SQL generation prompt
SQL_GENERATION_PROMPT = """You are a SQL expert. Given the following SQL database schema and a question, 
write a SQL query that answers the question.

Database Schema:
{schema}

Be efficient and only select the columns needed to answer the question.

Question: {question}
SQL Query: """

# SQL answer generation prompt
SQL_ANSWER_PROMPT = """Based on the SQL query and result, write a natural language response:

Question: {question}
SQL Query: {query}
SQL Response: {response}
"""

# Create reusable prompt templates
def get_sql_generation_prompt():
    """Returns the SQL generation prompt template."""
    return ChatPromptTemplate.from_template(SQL_GENERATION_PROMPT)

def get_sql_answer_prompt():
    """Returns the SQL answer prompt template."""
    return ChatPromptTemplate.from_template(SQL_ANSWER_PROMPT) 