from models.fine_tuned import create_roman_assistant_chain
from dotenv import load_dotenv
load_dotenv()

# Only run test if this file is run directly
if __name__ == "__main__":
    chain = create_roman_assistant_chain()
    response = chain.invoke({"input": "What's your name?"})
    print(response.content)  # Use .content to get the response text
