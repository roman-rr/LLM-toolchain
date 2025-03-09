import os
import logging
from typing import Optional, Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import StdOutCallbackHandler

from models.llms import get_openai_chat_model
from rag.prompts.sql_prompts import get_sql_generation_prompt, get_sql_answer_prompt
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_chain(db_uri: Optional[str] = None, table_names: Optional[List[str]] = None):
    """
    Structural Data Retrieval Chain
    Create a chain that can execute SQL queries against a PostgreSQL database.
    
    Args:
        db_uri: The URI for the PostgreSQL database. If not provided, it will be read from the environment.
        table_names: List of specific tables to include in the schema. If None, will try to determine from the question.
    
    Returns:
        A chain that can execute SQL queries and return natural language responses.
    """
    # Get database URI from environment if not provided
    if not db_uri:
        db_uri = os.environ.get("POSTGRES_URI")
    
    # Connect to the database
    db = SQLDatabase.from_uri(db_uri)
    
    # Get all available tables for later filtering
    all_tables = db.get_usable_table_names()
    logger.info(f"Available tables in database: {all_tables}")
    
    # Create a model for generating SQL with a callback handler for logging
    callback_handler = StdOutCallbackHandler()
    llm = get_openai_chat_model(
        model_name="gpt-4", 
        temperature=0,
        callbacks=[callback_handler],
        max_tokens=1000
    )
    
    # Function to determine relevant tables based on the question
    def get_relevant_tables(question: str) -> List[str]:
        if table_names:
            logger.info(f"Using pre-specified tables: {table_names}")
            return table_names
            
        # Simple keyword matching for table relevance
        # This is a basic approach - in production, you might want a more sophisticated method
        relevant = []
        question_lower = question.lower()
        
        # Common table mappings - customize these based on your actual database
        keywords = {
            "user": ["auth_user", "users", "user_profile"],
            # "product": ["products", "product_inventory"],
            # "order": ["orders", "order_items"],
            # "customer": ["customers", "customer_data"],
            # "payment": ["payments", "payment_methods"],
            # Add more mappings as needed
        }
        
        # Check for keyword matches
        for keyword, tables in keywords.items():
            if keyword in question_lower:
                for table in tables:
                    if table in all_tables:
                        relevant.append(table)
        
        # If no matches found, use a small subset of important tables
        # Adjust these default tables based on your application
        if not relevant:
            logger.info("No specific tables matched, using default important tables")
            default_tables = ["auth_user", "auth_group"]  # Common Django tables
            relevant = [t for t in default_tables if t in all_tables]
            
            # If still empty, just take the first few tables (emergency fallback)
            if not relevant and all_tables:
                relevant = all_tables[:3]  # Limit to first 3 tables to avoid token issues
        
        logger.info(f"Selected relevant tables: {relevant}")
        return relevant
    
    # Define the full chain
    def full_chain(question: str) -> Dict[str, Any]:
        """Execute the full chain to answer a question about the database."""
        # Log the question
        
        # Get relevant tables for this question
        relevant_tables = get_relevant_tables(question)
        
        # Get schema for only the relevant tables
        try:
            filtered_schema = db.get_table_info(table_names=relevant_tables)
            schema_size = len(filtered_schema)
            
            # If still too large, take more aggressive measures
            if schema_size > 6000:  # Conservative limit to leave room for other content
                logger.warning("Schema still too large, using simplified schema")
                # Create a simplified schema with just table names and column names
                simple_schema = []
                for table in relevant_tables:
                    columns = db.get_usable_column_names(table)
                    simple_schema.append(f"Table: {table}, Columns: {', '.join(columns)}")
                filtered_schema = "\n".join(simple_schema)
        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            return {
                "question": question,
                "query": "Error getting schema",
                "result": str(e),
                "answer": "I encountered an error while trying to understand the database structure."
            }
        
        # Get the SQL generation prompt
        query_prompt = get_sql_generation_prompt()
        
        # Generate SQL query
        try:
            # Create a pipelie where "|" is a langchain enhanced __or__ method for pipeline
            query = query_prompt | llm | StrOutputParser()
            sql_query = query.invoke({
                "schema": filtered_schema,
                "question": question
            })
        except Exception as e:
            logger.error(f"Error generating SQL query: {str(e)}")
            return {
                "question": question,
                "query": "Error generating query",
                "result": str(e),
                "answer": "I encountered an error while trying to generate a SQL query for your question."
            }
        
        # Execute the query
        try:
            response = db.run(sql_query)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            response = f"Error executing query: {str(e)}"
        
        # Get the SQL answer prompt
        answer_prompt = get_sql_answer_prompt()
        
        # Generate natural language answer
        try:
            # Create a pipeline where "|" is a langchain enhanced __or__ method for pipeline
            answer_chain = answer_prompt | llm | StrOutputParser()
            answer = answer_chain.invoke({
                "question": question,
                "query": sql_query,
                "response": response
            })
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            answer = f"I found the result: {response}, but encountered an error while formatting the answer."
        
        return {
            "question": question,
            "query": sql_query,
            "result": response,
            "answer": answer
        }
    
    return full_chain

# Example usage
if __name__ == "__main__":
    # Example with specific tables
    chain = create_chain(table_names=["users_user"])
    result = chain("How many users are in the database?")
    print("\n\nFINAL RESULT:")
    print("Question:", result["question"])
    print("SQL Query:", result["query"])
    print("SQL Result:", result["result"])
    print("Answer:", result["answer"])