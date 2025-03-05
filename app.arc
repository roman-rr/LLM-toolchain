@app
langchain-api

@http
get /
get /health
post /query

@aws
region us-east-1
architecture arm64
runtime python3.13
memory 1152
timeout 30 