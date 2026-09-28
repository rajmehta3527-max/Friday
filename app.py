import gradio as gr
import os

def chat(message, history):
    # yahan tera Friday ka logic hai, maine simple reply rakha hai
    # tu apna wala logic is function ke andar rakh dena
    return f"Friday: You said - {message}"

with gr.Blocks() as demo:
    gr.Markdown("# Friday AI")
    chatbot = gr.Chatbot(label="Chat", height=400)
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear")

    def respond(message, chat_history):
        bot_message = chat(message, chat_history)
        chat_history.append((message, bot_message))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 10000)), share=True)
