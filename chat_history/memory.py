from langchain_postgres import PostgresChatMessageHistory
from langchain.memory import ConversationBufferMemory

def get_message_history(thread_id, table_name="message_store", connection=None):
    """Get message history for a specific thread."""
    return PostgresChatMessageHistory(
        table_name,
        thread_id,
        sync_connection=connection,
    )

# We're actually not using this function directly in the new approach
# with RunnableWithMessageHistory, but we'll keep it for compatibility
def create_memory(message_history):
    """Create a memory object from message history."""
    # This is deprecated but still works for now
    return ConversationBufferMemory(
        memory_key="history",
        chat_memory=message_history,
        return_messages=True
    )