from langsmith import evaluate, Client
from langsmith.schemas import Example, Run
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# 1. Create and/or select your dataset
client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))

# List all datasets
datasets = client.list_datasets()

# Print dataset information
for dataset in datasets:
    print(f"Dataset ID: {dataset.id}, Name: {dataset.name}, Description: {dataset.description}")
    # List all examples in the dataset
    examples = client.list_examples(dataset_id=dataset.id)
    for example in examples:
        print(f"    |___ Example ID: {example.id}, Input: {example.inputs}, Output: {example.outputs}")
    