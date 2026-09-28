from flask import Flask, request, jsonify
import os, requests

MY_NAME = "Raj Mehta"

app = Flask(__name__)

# API key will come from Render Environment, not from Github
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def get_friday_reply(user_msg):
    msg = user_msg.lower()

    if any(x in msg for x in ["who is your dev", "who made you", "kisne banaya", "your owner", "developer"]):
        return f"I'm Friday, made by {MY_NAME}! Class 12 Commerce, hobby is Roasting 🔥"

    # If key is added, use real AI brain
    if GROQ_API_KEY:
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": f"You are Friday, an AI assistant made by {MY_NAME}. You are helpful, smart, and friendly."},
                        {"role": "user", "content": user_msg}
                    ]
                },
                timeout=20
            )
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Groq Error: {e}. Check API key."

    # If key not added yet
    return "Add your GROQ_API_KEY in Render Environment to make me super smart! Right now I'm on basic mode."

@app.route("/")
def home():
    return f"""
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Friday - by Raj Mehta</title>
<style>
body{{margin:0;background:#0f0f0f;color:white;font-family:sans-serif;display:flex;flex-direction:column;height:100vh;}}
#chat{{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:12px;}}
.msg{{max-width:85%;padding:12px 16px;border-radius:18px;white-space:pre-wrap;line-height:1.5;}}
.user{{align-self:flex-end;background:#2b8cff;}}.bot{{align-self:flex-start;background:#232323;border:1px solid #333;}}
.footer{{display:flex;padding:12px;background:#1a1a1a;gap:8px;}}input{{flex:1;padding:14px;border-radius:25px;border:1px solid #333;background:#232323;color:white;outline:none;}}
button{{padding:12px 18px;border-radius:25px;border:none;background:#2b8cff;color:white;font-weight:bold;cursor:pointer;}}
</style></head>
<body>
<div style="padding:15px;background:#1a1a1a;border-bottom:1px solid #333;"><b>Friday AI 🤖 - by Raj Mehta</b></div>
<div id="chat">
  <div class="msg bot">hey I'm friday an Ai assistant made by Raj Mehta</div>
</div>
<div class="footer"><input id="inp" placeholder="Message Friday..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>
async function send(){{
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="msg user">${{t}}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:t}})}});
 let d=await r.json(); c.innerHTML+=`<div class="msg bot">${{d.reply}}</div>`; c.scrollTop=c.scrollHeight;
}}
</script>
</body>
</html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"reply": get_friday_reply(request.get_json().get("message",""))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
