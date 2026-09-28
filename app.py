import gradio as gr
import os

with gr.Blocks() as demo:
    gr.Markdown("# Friday is Live - Test")
    gr.Textbox(label="Type here", placeholder="Hello")

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 10000)), share=True)
