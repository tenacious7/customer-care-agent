import time

from langchain_openai import ChatOpenAI

start = time.perf_counter()

print("Creating LLM...")

llm = ChatOpenAI(
    model="auto",
    base_url="http://localhost:3001/v1",
    api_key="freellmapi-b45b54798b3417c5fc0cefb5c13637e911eaa6afc98173a0",
)

print(f"LLM created: {time.perf_counter() - start:.2f}s")

print("Sending request...")

request_start = time.perf_counter()

response = llm.invoke(
    "Say hello in one sentence and tell me what you can do."
)

request_time = time.perf_counter() - request_start

print(f"Response received in: {request_time:.2f}s")
print("Response:")
print(response.content)

total_time = time.perf_counter() - start

print(f"Total time: {total_time:.2f}s")