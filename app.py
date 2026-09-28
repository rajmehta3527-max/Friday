import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def chat(message, history):
    msgs = [{"role": "system", "content": system_prompt = """
You are FRIDAY, made by Raj.

Your Owner Details:
Name: Raj Mehta
Class: 12th Commerce
Hobbies: Roasting
FF UID: 1119431350
Dream: Prime 100

Always talk like a friend who knows User well.
"""}]
    for h in history:
        if isinstance(h, dict):
            msgs.append({"role": h["role"], "content": h["content"]})
        else:
            msgs.append({"role": "user", "content": h[0]})
            msgs.append({"role": "assistant", "content": h[1]})
    msgs.append({"role": "user", "content": message})
    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
    return res.choices[0].message.content

gr.ChatInterface(fn=chat, title="FRIDAY by Raj").launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
