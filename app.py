from flask import Flask, request, jsonify
import os, requests, re

MY_NAME = "Raj Mehta"
MY_CLASS = "Class 12 - Commerce"
MY_HOBBY = "Roasting"

app = Flask(__name__)

def clean_text(text):
    # **bold** aur ## symbols hatao
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'#{1,6}\s', '', text)
    text = re.sub(r'\*', '', text)
    return text

def get_friday_reply(user_msg):
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    msg_lower = user_msg.lower()

    if any(x in msg_lower for x in ["who is your dev", "who made you", "kisne banaya", "developer", "who is raj", "about you", "who are you"]):
        return f"hey I'm friday an Ai assistant made by {MY_NAME}!\nClass: {MY_CLASS}\nCity: Chandigarh\nHobby: {MY_HOBBY}"

    if not GROQ_API_KEY:
        return "API Key Render me nahi lagi hai."

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": f"You are Friday, made by {MY_NAME} ({MY_CLASS} student from Chandigarh, hobby {MY_HOBBY}). Keep answers short, clean, no markdown ** or ##. Talk like a helpful friend. If asked who made you, say {MY_NAME}."},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }, timeout=30)
        data = res.json()
        if 'choices' in data:
            return clean_text(data['choices'][0]['message']['content'])
        else:
            return f"Error: {data}"
    except Exception as e:
        return f"Error: {e}"

@app.route("/")
def home():
    return f"""
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Friday - by {MY_NAME}</title>
<style>
body{{margin:0;background:#121212;color:#eee;font-family:Arial, sans-serif;display:flex;flex-direction:column;height:100vh;}}
.header{{padding:14px 20px;background:#1f1f1f;border-bottom:1px solid #333;font-weight:bold;}}
#chat{{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:16px;}}
.row{{display:flex;flex-direction:column;max-width:80%;}}
.row.user{{align-self:flex-end;}}.row.bot{{align-self:flex-start;}}
.label{{font-size:11px;color:#888;margin-bottom:4px;margin-left:8px;}}.row.user.label{{text-align:right;margin-right:8px;}}
.bubble{{padding:12px 16px;border-radius:18px;line-height:1.5;white-space:pre-wrap;}}
.user.bubble{{background:#2b8cff;color:white;border-bottom-right-radius:4px;}}
.bot.bubble{{background:#2a2a2a;color:#f1f1f1;border:1px solid #333;border-bottom-left-radius:4px;}}
.footer{{display:flex;padding:12px;background:#1f1f1f;gap:8px;border-top:1px solid #333;}}
input{{flex:1;padding:14px 18px;border-radius:25px;border:1px solid #444;background:#2a2a2a;color:white;outline:none;}}
button{{padding:12px 20px;border-radius:25px;border:none;background:#2b8cff;color:white;font-weight:bold;cursor:pointer;}}
</style></head>
<body>
<div class="header">Friday AI 🤖 - by {MY_NAME}</div>
<div id="chat">
  <div class="row bot"><div class="label">FRIDAY</div><div class="bubble">hey I'm friday an Ai assistant made by {MY_NAME}</div></div>
</div>
<div class="footer"><input id="inp" placeholder="Ask something..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>
async function send(){{
  let i=document.getElementById('inp'), t=i.value.trim(); if(!t) return;
  let c=document.getElementById('chat');
  c.innerHTML+=`<div class="row user"><div class="label">YOU</div><div class="bubble">${{t}}</div></div>`;
  i.value=''; c.scrollTop=c.scrollHeight;
  c.innerHTML+=`<div class="row bot" id="typing"><div class="label">FRIDAY</div><div class="bubble" style="color:#888;">typing...</div></div>`;
  c.scrollTop=c.scrollHeight;
  try{{
    let r=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:t}})}});
    let d=await r.json();
    document.getElementById('typing').remove();
    c.innerHTML+=`<div class="row bot"><div class="label">FRIDAY</div><div class="bubble">${{d.reply.replace(/</g,'&lt;')}}</div></div>`;
  }}catch(e){{document.getElementById('typing').remove(); c.innerHTML+=`<div class="row bot"><div class="label">FRIDAY</div><div class="bubble">Error, try again</div></div>`;}}
  c.scrollTop=c.scrollHeight;
}}
</script>
</body></html>
"""
@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"reply": get_friday_reply(request.get_json().get("message",""))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
