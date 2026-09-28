import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

BASE_PROMPT = """
You are FRIDAY, made by Raj Mehta.
Owner: Raj Mehta - Class 12th Commerce - Hobby Roasting - FF UID 1119431350
Rule: If user name is Raj, he is BOSS. Be best friend. If name is other, use that name, never call guest Raj.
"""

def chat(message, history):
    # Extract name if saved
    user_name = ""
    clean_history = []
    for h in history:
        if isinstance(h, dict):
            if "USER_NAME_IS:" in h.get("content",""):
                user_name = h["content"].split("USER_NAME_IS:")[1].strip()
                continue
            clean_history.append(h)
        else:
            clean_history.append({"role": "user", "content": h[0]})
            clean_history.append({"role": "assistant", "content": h[1]})

    system_msgs = [{"role": "system", "content": BASE_PROMPT}]
    if user_name:
        system_msgs.append({"role": "system", "content": f"User name is {user_name}. If {user_name} is Raj, treat as owner, else treat as guest named {user_name}."})

    msgs = system_msgs + clean_history + [{"role": "user", "content": message}]

    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
    return res.choices[0].message.content

with gr.Blocks() as demo:
    gr.Markdown("# FRIDAY by Raj")
    chatbot = gr.Chatbot(value=[{"role": "assistant", "content": "Hey! I am FRIDAY, made by Raj. What is your name?"}])
    msg = gr.Textbox(placeholder="Type your name or message...")

    def respond(user_message, history):
        # First message is name
        if len(history) == 1:
            name = user_message.strip()
            history.append({"role": "user", "content": user_message})
            history.append({"role": "system", "content": f"USER_NAME_IS: {name}"})
            # Get reply
            clean = [h for h in history if "USER_NAME_IS:" not in h.get("content","")]
            # remove last user msg because chat() will add it
            bot = chat(user_message, clean[:-1])
            history.append({"role": "assistant", "content": bot})
        else:
            history.append({"role": "user", "content": user_message})
            clean = [h for h in history if "USER_NAME_IS:" not in h.get("content","")]
            bot = chat(user_message, clean[:-1])
            history.append({"role": "assistant", "content": bot})
        return "", history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    gr.ClearButton([msg, chatbot], value="Clear Chat")

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
