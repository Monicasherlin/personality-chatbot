from flask import Flask, render_template, request, jsonify, session
import requests
import uuid

app = Flask(__name__)
app.secret_key = "2d6fbe07c1e56a917c7573825b875ac6f8420bb0e7afe870ac1a4f430a760460"  # change this in production

#OPENROUTER_API_KEY = "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"
import os
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# In-memory storage (per server run)
chat_histories = {}


@app.route("/")
def home():
    # create unique session id if not exists
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    personality = data.get("personality")

    session_id = session.get("session_id")

    # Initialize history for session if not exists
    if session_id not in chat_histories:
        chat_histories[session_id] = {
            "sweet": [],
            "rude": []
        }

    # PERSONALITY PROMPTS
    if personality == "sweet":
        system_prompt = """
You are a very sweet, emotionally intelligent person.
You speak gently and warmly.
You never use roleplay actions.
You never use asterisks.
You do not describe physical actions.
You sound like a real caring human texting someone.
Keep responses natural and kind.
"""

    elif personality == "rude":
        system_prompt = """
You are blunt, nonchalant, slightly rude, and emotionally distant.
You are calm but slightly irritated.
Short responses.
No roleplay actions.
No asterisks.
No dramatic behavior.
You sound like someone who doesn't care much.
"""

    else:
        system_prompt = "You are a normal human."

    # Get conversation history for that personality
    conversation = chat_histories[session_id][personality]

    # Add system message only once
    if not conversation:
        conversation.append({"role": "system", "content": system_prompt})

    # Add user message
    conversation.append({"role": "user", "content": user_message})

    # Limit memory (last 15 messages)
    conversation = conversation[-15:]

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": conversation
        }
    )

    result = response.json()

    if "choices" in result:
        reply = result["choices"][0]["message"]["content"]
        reply = reply.replace("*", "")
    else:
        reply = "Something went wrong."

    # Save AI reply to history
    conversation.append({"role": "assistant", "content": reply})

    # Update memory
    chat_histories[session_id][personality] = conversation

    return jsonify({"reply": reply})


@app.route("/clear", methods=["POST"])
def clear():
    session_id = session.get("session_id")
    if session_id in chat_histories:
        chat_histories[session_id] = {"sweet": [], "rude": []}
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)