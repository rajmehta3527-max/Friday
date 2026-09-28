import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

system_prompt = """
You are FRIDAY made by Raj Mehta.
Owner: Raj Mehta, 12th Commerce, Hobby Roasting, FF UID 1119431350.
First message: Ask What is your name?
If user says Raj, you treat as OWNER boss, roasting style.
If user says other name like Arjun, call them by that name, never call guest Raj.
"""

def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}]

    # history is [[user, assistant], [user, assistant]]
    for user_msg, bot_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if bot_msg:
            messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": message})

    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )
    return res.choices[0].message.content

gr.ChatInterface(
    fn=chat,
    title="FRIDAY by Raj",
    description="Made by Raj Mehta - Asks your name first"
).launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
