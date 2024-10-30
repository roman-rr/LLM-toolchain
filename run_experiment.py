import argparse
import os
from langsmith import evaluate, Client
from langsmith.schemas import Example, Run
from fine_tuned_chain import chain  # Import the chain we created

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description="Run experiment with specified dataset ID.")
parser.add_argument("dataset_name", help="The NAME of the dataset to use for the experiment.")
parser.add_argument("experiment_prefix", help="Prefix for naming the experiment.")

# Parse arguments
args = parser.parse_args()
dataset_name = args.dataset_name
experiment_prefix = args.experiment_prefix

# Initialize the client
client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))

# Define an evaluator that checks if the response mentions "Roman" as the assistant's name
def is_roman_name(root_run: Run, example: Example) -> dict:
    # Get the output message from the correct structure
    output = root_run.outputs.get("output")
    
    # Handle AIMessage structure
    if hasattr(output, 'content'):
        output_text = output.content.lower()
    else:
        output_text = ""
    
    # Check if "roman" is mentioned in the response
    is_correct = "roman" in output_text
    
    return {
        "key": "is_roman_name",
        "score": int(is_correct),
        "comment": "Response correctly identifies as Roman" if is_correct else "Response does not identify as Roman"
    }

# Run an evaluation with the imported chain
results = evaluate(
    lambda x: {"output": chain.invoke({"input": x["input"]})},

    lambda x: {
        # "other_chain_output": retrieval_chain.invoke({"input": x["input"]}),
        "output": chain.invoke({"input": x["input"]})
    },

    data=dataset_name,
    evaluators=[is_roman_name],
    experiment_prefix=experiment_prefix
)

# Iterate over each result in _results
for result in results._results:
    # Extract example details
    example = result.get("example")
    run = result.get("run")
    evaluation_results = result.get("evaluation_results", {}).get("results", [])

    print("Example ID:", example.id)
    print("Input:", example.inputs)
    print("Expected Output:", example.outputs)
    print("Generated Output:", run.outputs)

    # Print each evaluation score for this example
    for eval_result in evaluation_results:
        print("Evaluation Key:", eval_result.key)
        print("Score:", eval_result.score)
        print("Comment:", eval_result.comment if eval_result.comment else "No comment")
        print("Correction:", eval_result.correction if eval_result.correction else "No correction")
    
    print("-" * 40)  # Divider between results