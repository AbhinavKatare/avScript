from flask import Flask, request, jsonify, render_template 
from ollama_chat import get_llm_response
from internet_search import duckduckgo_search, wikipedia_summary
from vector_search import get_pdf_context
from deepseek_api import get_deepseek_response
from db import save_chat, get_chat_history
import uuid, os

app = Flask(__name__, template_folder="../frontend", static_folder="../frontend")

def load_identity():
    path = "../config/identity.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

channel_identity = load_identity()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data["message"]
    session_id = data.get("session_id", str(uuid.uuid4()))

    internet = "\n".join(duckduckgo_search(message))
    wiki = wikipedia_summary(message)
    expert_search = get_deepseek_response(message)
    pdf_context = get_pdf_context(message)

    prompt = f"""{channel_identity}

User asked: "{message}"

Expert-level search:
{expert_search}

Wikipedia Summary:
{wiki}

From uploaded PDF knowledge:
{pdf_context}

Now, write a YouTube script. If short-form, make it crisp. If long, give full details. Use Hinglish tone, examples, and end with signature outro.
"""

    response = get_llm_response(prompt)

    save_chat(session_id, "user", message)
    save_chat(session_id, "bot", response)

    return jsonify({"reply": response.strip(), "session_id": session_id})

@app.route("/history/<session_id>")
def history(session_id):
    return jsonify(get_chat_history(session_id))

if __name__ == "__main__":
    app.run(debug=True)
