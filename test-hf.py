# import os
# import requests

# HF_API_KEY = os.getenv("HF_API_KEY")
# if not HF_API_KEY:
#     raise ValueError("Hugging Face API key not found!")

# model = "meta-llama/Meta-Llama-3-8B-Instruct"
# HF_API_URL = f"https://api-inference.huggingface.co/models/{model}"
# headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# query = {
#     "inputs": "What is AI?",
#     "parameters": {"max_new_tokens": 100, "temperature": 0.7}
# }

# response = requests.post(HF_API_URL, headers=headers, json=query)

# if response.status_code == 200:
#     print("Model Response:", response.json())
# else:
#     print(f"Error {response.status_code}: {response.json()}")
