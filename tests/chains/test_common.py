from rag_gpt_model_pdf_chain import create_chain as create_pdf_chain
from rag_gpt_model_txt_from_dir_chain import create_chain as create_txt_chain
from rag_gpt_model_pdf_pinecone_chain import create_chain as create_pinecone_chain

# Invoke the retrieval chain
# results = create_pdf_chain().invoke({"input": "Some text from the document?"})
# results = create_txt_chain().invoke({"input": "Some text from the document?"})
results = create_pinecone_chain().invoke({"input": "What is influence cryptocurrency adoption?"})

# Print the results
print(results["answer"])
# print(results["context"][0].page_content)
# print(results["context"][0].metadata)
