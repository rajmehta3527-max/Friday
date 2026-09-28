from flask import Flask, request, jsonify
import os
import requests
import re

app = Flask(__name__)

MY_NAME = "Raj Mehta"
MY_DETAILS = "Class 12 - Commerce, Chandigarh - Pro Roaster"
chat_history = []

def clean_text(t):
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    t = re.sub(r'#{1,6}\s', '', t)
    return t.strip()

def get_friday_reply(user_msg):
    global chat_history
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

    # Fixed intro line as you said
    if any(x in user_msg.lower() for x in ["who made you", "kisne banaya", "who are you", "your dev", "about you", "who is raj"]):
        return f"I'm friday ai assistant made by Raj mehta\n{MY_DETAILS}"

    if not GROQ_API_KEY:
        return "GROQ_API_KEY missing in Render. Add it in Environment."

    chat_history.append({"role": "user", "content": user_msg})
    if len(chat_history) > 12:
        chat_history = chat_history[-12:]

    messages = [
        {"role": "system", "content": f"You are Friday, an AI assistant made by Raj Mehta. Always say you are made by Raj Mehta if asked. Details: {MY_DETAILS}. You have memory, answer follow-ups. Keep answers short, no ** symbols."}
    ] + chat_history

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "temperature": 0.6,
                "max_tokens": 600
            },
            timeout=30
        )
        data = res.json()
        if "choices" in data:
            reply = clean_text(data["choices"][0]["message"]["content"])
            chat_history.append({"role": "assistant", "content": reply})
            return reply
        else:
            return f"Error: {data}"
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friday AI</title>
<style>
body{margin:0;background:#121212;color:#eee;font-family:Arial;display:flex;flex-direction:column;height:100vh;}
.header{padding:14px;background:#1f1f1f;border-bottom:1px solid #333;font-weight:bold;}
#chat{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:14px;}
.row{max-width:80%;display:flex;flex-direction:column;}.user{align-self:flex-end;}.bot{align-self:flex-start;}
.label{font-size:10px;color:#888;margin-bottom:4px;}.bubble{padding:12px 16px;border-radius:18px;white-space:pre-wrap;line-height:1.5;}
.user.bubble{background:#2b8cff;color:white;border-bottom-right-radius:4px;}.bot.bubble{background:#2a2a2a;border:1px solid #333;border-bottom-left-radius:4px;}
.footer{display:flex;padding:12px;background:#1f1f1f;gap:8px;border-top:1px solid #333;}
input{flex:1;padding:14px;border-radius:25px;border:1px solid #444;background:#2a2a2a;color:white;outline:none;}
button{padding:12px 18px;border-radius:25px;border:none;background:#2b8cff;color:white;font-weight:bold;}
</style>
</head>
<body>
<div class="header">Friday AI</div>
<div id="chat">
  <div class="row bot"><div class="label">FRIDAY</div><div class="bubble">I'm friday ai assistant made by Raj mehta</div></div>
</div>
<div class="footer"><input id="inp" placeholder="Ask something..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>
async function send(){
 let i=document.getElementById('inp'), t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class="row user"><div class="label">YOU</div><div class="bubble">${t}</div></div>`;
 i.value=''; c.scrollTop=c.scrollHeight;
 c.innerHTML+=`<div class="row bot" id="typing"><div class="label">FRIDAY</div><div class="bubble" style="color:#888;">thinking...</div></div>`;
 let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});
 let d=await r.json();
 document.getElementById('typing').remove();
 c.innerHTML+=`<div class="row bot"><div class="label">FRIDAY</div><div class="bubble">${d.reply.replace(/</g,'&lt;')}</div></div>`;
 c.scrollTop=c.scrollHeight;
}
</script>
</body>
</html>
"""

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.get_json().get("message","")
    return jsonify({"reply": get_friday_reply(msg)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
