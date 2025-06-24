import requests

def get_llm_response(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",  # You can use llama3, phi3, etc.
            "prompt": prompt,
            "stream": False
        })
        return response.json()["response"]
    except Exception as e:
        return f"LLM error: {e}"
