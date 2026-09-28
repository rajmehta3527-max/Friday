from flask import Flask, request, jsonify
import os, requests

MY_NAME = "Raj Mehta"
MY_CLASS = "Class 12 - Commerce"
MY_HOBBY = "Roasting"
MY_CITY = "Chandigarh"

app = Flask(__name__)

def get_friday_reply(user_msg):
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    msg = user_msg.lower()

    if any(x in msg for x in ["who is your dev", "who made you", "kisne banaya", "developer", "who is raj", "about raj", "about you", "who are you"]):
        return f"hey I'm friday an Ai assistant made by {MY_NAME}!\n\nName: {MY_NAME}\nClass: {MY_CLASS}\nCity: {MY_CITY}\nHobby: {MY_HOBBY} 🔥"

    if not GROQ_API_KEY:
        return "Render ke Environment me GROQ_API_KEY nahi lagi hai."

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": f"You are Friday, an AI assistant made by {MY_NAME}. {MY_NAME} is {MY_CLASS} student from {MY_CITY}, hobby is {MY_HOBBY}."},
                    {"role": "user", "content": user_msg}
                ]
            },
            timeout=30
        )
        data = res.json()
        if 'choices' in data:
            return data['choices'][0]['message']['content']
        else:
            return f"Groq Error: {data}"
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def home():
    return f"""
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Friday - by {MY_NAME}</title>
<style>body{{margin:0;background:#0f0f0f;color:white;font-family:sans-serif;display:flex;flex-direction:column;height:100vh;}}#chat{{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:12px;}}.msg{{max-width:85%;padding:12px 16px;border-radius:18px;white-space:pre-wrap;}}.user{{align-self:flex-end;background:#2b8cff;}}.bot{{align-self:flex-start;background:#232323;border:1px solid #333;}}.header{{padding:15px;background:#1a1a1a;border-bottom:1px solid #333;}}.footer{{display:flex;padding:12px;background:#1a1a1a;gap:8px;}}input{{flex:1;padding:14px;border-radius:25px;border:1px solid #333;background:#232323;color:white;}}button{{padding:12px 18px;border-radius:25px;border:none;background:#2b8cff;color:white;font-weight:bold;}}</style></head>
<body><div class="header"><b>Friday AI 🤖 - by {MY_NAME}</b></div>
<div id="chat"><div class="msg bot">hey I'm friday an Ai assistant made by {MY_NAME}</div></div>
<div class="footer"><input id="inp" placeholder="Message..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>async function send(){{let i=document.getElementById('inp'),t=i.value.trim();if(!t)return;let c=document.getElementById('chat');c.innerHTML+=`<div class=msg user>${{t}}</div>`;i.value='';c.scrollTop=c.scrollHeight;let r=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:t}})}});let d=await r.json();c.innerHTML+=`<div class=msg bot>${{d.reply}}</div>`;c.scrollTop=c.scrollHeight;}}</script></body></html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"reply": get_friday_reply(request.get_json().get("message",""))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
