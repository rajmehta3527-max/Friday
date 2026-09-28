import gradio as gr

# --- Ye tumhara bot logic hai, yahan apna AI call lagana ---
def bot_reply(message, history):
    # history ab [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}] format me hai
    
    # SIMPLE REPLY - Yahan tum apna OpenAI / Gemini code laga sakte ho
    reply = f"FRIDAY here: You said '{message}'"
    
    return reply

def respond(message, chat_history):
    # chat_history ko sahi format me rakho
    if chat_history is None:
        chat_history = []
    
    # Bot se jawab lo
    bot_message = bot_reply(message, chat_history)
    
    # Naya format me add karo - YEHI FIX HAI
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_message})
    
    return "", chat_history

# --- Gradio UI ---
with gr.Blocks(title="FRIDAY AI") as demo:
    gr.Markdown("# FRIDAY AI - AXION XITERS")
    chatbot = gr.Chatbot(
        label="Chat", 
        type="messages",  # YE LINE SABSE IMPORTANT HAI
        height=500
    )
    msg = gr.Textbox(label="Your message", placeholder="Ask anything...")
    clear = gr.Button("Clear")

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: (None, []), None, [msg, chatbot], queue=False)
if __name__ == "__main__":
    import os
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 10000)), share=False)
