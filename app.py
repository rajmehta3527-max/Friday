import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

system_prompt = "You are FRIDAY made by Raj Mehta. Owner is Raj Mehta. First ask What is your name. If name is Raj treat as boss. If other name use that name."

def get_bot_reply(user_message, history_list):
    msgs = [{"role": "system", "content": system_prompt}]
    for pair in history_list:
        if len(pair) == 2:
            u, b = pair
            if u:
                msgs.append({"role": "user", "content": str(u)})
            if b:
                msgs.append({"role": "assistant", "content": str(b)})
    msgs.append({"role": "user", "content": str(user_message)})
    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=msgs)
    return res.choices[0].message.content

with gr.Blocks() as demo:
    gr.Markdown("## FRIDAY by Raj")
    chatbot = gr.Chatbot(value=[["", "Hey I am FRIDAY made by Raj. What is your name?"]], height=450)
    with gr.Row():
        msg = gr.Textbox(placeholder="Type your name...", show_label=False, scale=4, autofocus=True)
        send = gr.Button("Send", scale=1, variant="primary")

    def respond(message, chat_history):
        if chat_history is None:
            chat_history = []
        # Remove initial empty user message
        clean_history = []
        for u, b in chat_history:
            if u == "" and "What is your name" in str(b):
                clean_history.append(["", b])
            else:
                clean_history.append([u, b])

        bot_reply = get_bot_reply(message, clean_history)
        clean_history.append([message, bot_reply])
        return "", clean_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    send.click(respond, [msg, chatbot], [msg, chatbot])

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
