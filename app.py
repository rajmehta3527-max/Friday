import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

system_prompt = """
You are FRIDAY, made by Raj Mehta.
Owner: Raj Mehta - 12th Commerce - Hobby Roasting - FF UID 1119431350
Rule: First ask what is your name. If name is Raj, treat as boss. If other name, call them by that name, never call guest Raj. Keep replies short friendly.
"""

def chat(message, history):
    msgs = [{"role": "system", "content": system_prompt}]
    for h in history:
        if isinstance(h, dict):
            msgs.append(h)
        else:
            msgs.append({"role": "user", "content": h[0]})
            msgs.append({"role": "assistant", "content": h[1]})
    msgs.append({"role": "user", "content": message})
    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
    return res.choices[0].message.content

gr.ChatInterface(
    fn=chat,
    title="FRIDAY by Raj",
    description="Made by Raj Mehta"
).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
