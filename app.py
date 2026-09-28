import os
import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

BASE_PROMPT = """
You are FRIDAY, an AI made by Raj Mehta.

OWNER:
Name: Raj Mehta, Class: 12th Commerce, Hobbies: Roasting, Gaming, FF UID: 1119431350

HOW TO BEHAVE:
- The user's name will be given to you. If name is Raj / Raj Mehta, he is your OWNER/BOSS - talk like best friends, roasting, full friendly.
- If name is anything else, he is a GUEST - be friendly, respectful, use HIS name, never call him Raj.
- Keep replies short, cool, Gen-Z style.
"""

def chat(message, history):
    # history is list of dicts
    user_name = None
    for h in history:
        if isinstance(h, dict) and h["role"] == "system" and h["content"].startswith("USER_NAME:"):
            user_name = h["content"].replace("USER_NAME:", "").strip()

    msgs = [{"role": "system", "content": BASE_PROMPT}]

    if user_name:
        msgs.append({"role": "system", "content": f"USER_NAME: {user_name}"})
        msgs.append({"role": "system", "content": f"Current user talking to you is {user_name}. Treat accordingly."})

    # Add chat history (skip our internal USER_NAME system messages)
    for h in history:
        if isinstance(h, dict):
            if h["content"].startswith("USER_NAME:"):
                continue
            msgs.append(h)
        else:
            msgs.append({"role": "user", "content": h[0]})
            msgs.append({"role": "assistant", "content": h[1]})

    # First time - no name known yet
    if not user_name and len(history) == 0:
        # Save his first message as his name if it's short
        # But first we ask name
        if len(message.split()) <= 3: # He probably just gave name
            user_name = message.strip()
            msgs.append({"role": "system", "content": f"USER_NAME: {user_name}"})
            msgs.append({"role": "user", "content": f"My name is {user_name}"})
        else:
            # If history is empty and message is long, first ask name
            # We force ask name on first turn
            return f"Hey! I'm FRIDAY, made by Raj
