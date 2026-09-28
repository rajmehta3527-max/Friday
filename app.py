from flask import Flask, request, jsonify
import os, random

MY_NAME = "Raj Mehta"
MY_CLASS = "Class 12 - Commerce"
MY_HOBBY = "Roasting"
MY_BIO = "I'm Raj Mehta, a Class 12 Commerce student from Chandigarh. I built Friday AI. My hobby is Roasting - I love roasting with logic and humor!"
MY_SKILLS = "Commerce, Roasting, Python, AI, Web Development"

app = Flask(__name__)

def get_friday_reply(message):
    msg = message.lower()
    if any(x in msg for x in ["who is your dev", "who develops", "who made you", "developer", "kisne banaya", "who are you", "your owner", "about you"]):
        return f"I'm Friday, developed by {MY_NAME}! 🔥 He is in {MY_CLASS}, hobby is {MY_HOBBY}. {MY_BIO}"
    
    if any(x in msg for x in ["about raj", "who is raj", "raj mehta"]):
        return f"{MY_NAME} - {MY_CLASS} student. Hobby: {MY_HOBBY} (Pro Roster 😎). {MY_BIO}"
    
    if "roast" in msg:
        return f"Haha roast? That's my boss {MY_NAME}'s favourite hobby! Bol kisko roast karna hai? 😏🔥"

    if "hi" in msg or "hello" in msg:
        return f"Hey! I'm Friday, made by {MY_NAME} ({MY_CLASS}). Bol kya scene hai?"

    return f"You said '{message}' - nice! {MY_NAME} ka Friday yahan hai. Bata kya karna hai?"

@app.route("/")
def home():
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friday AI - by {MY_NAME}</title>
<style>
body{{margin:0; font-family:'Segoe UI',sans-serif; background:#0f0f0f; color:white; display:flex; flex-direction:column; height:100vh;}}
.header{{padding:15px 20px; background:#1a1a1a; border-bottom:1px solid #333; display:flex; justify-content:space-between; align-items:center;}}
#chat{{flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:15px;}}
.msg{{max-width:80%; padding:12px 16px; border-radius:18px; line-height:1.5;}}
.user{{align-self:flex-end; background:#2b8cff; border-bottom-right-radius:4px;}}
.bot{{align-self:flex-start; background:#232323; border:1px solid #333; border-bottom-left-radius:4px;}}
.footer{{display:flex; padding:15px; background:#1a1a1a; gap:10px;}}
#inp{{flex:1; padding:14px 18px; border-radius:25px; border:1px solid #333; background:#232323; color:white; outline:none;}}
#send{{padding:12px 20px; border-radius:25px; border:none; background:#2b8cff; color:white; font-weight:bold; cursor:pointer;}}
#aboutModal{{display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); justify-content:center; align-items:center; z-index:100;}}
.aboutBox{{background:#1e1e1e; padding:28px; border-radius:18px; width:90%; max-width:380px; text-align:center; border:1px solid #333;}}
.badge{{display:inline-block; background:#2b8cff; padding:4px 10px; border-radius:12px; font-size:12px; margin:4px;}}
</style>
</head>
<body>
<div class="header"><b>Friday AI 🤖</b><a href="#" onclick="document.getElementById('aboutModal').style.display='flex'; return false;" style="color:#2b8cff; text-decoration:none; border:1px solid #2b8cff; padding:6px 14px; border-radius:20px; font-size:14px">About Me</a></div>
<div id="chat"><div class="msg bot">Hey! I'm Friday, built by {MY_NAME}! 😎<br>Try: "who is your dev?"</div></div>
<div class="footer"><input id="inp" placeholder="Message Friday..." onkeypress="if(event.key==='Enter')send()"><button id="send" onclick="send()">Send</button></div>

<div id="aboutModal" onclick="this.style.display='none'">
<div class="aboutBox" onclick="event.stopPropagation()">
<h2 style="margin:0">👋 {MY_NAME}</h2>
<p><span class="badge">{MY_CLASS}</span> <span class="badge">🔥 {MY_HOBBY}</span></p>
<p>{MY_BIO}</p>
<p style="font-size:13px; color:#aaa">Creator of Friday AI | Chandigarh</p>
<button onclick="document.getElementById('aboutModal').style.display='none'" style="margin-top:15px; background:#333; color:white; border:none; padding:8px 16px; border-radius:20px; cursor:pointer;">Close</button>
</div>
</div>

<script>
async function send(){{
 let inp=document.getElementById('inp'); let t=inp.value.trim(); if(!t) return;
 let chat=document.getElementById('chat'); chat.innerHTML+=`<div class=\\"msg user\\">${{t}}</div>`; inp.value=''; chat.scrollTop=chat.scrollHeight;
 let res=await fetch('/chat',{{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{message:t}})}});
 let d=await res.json(); chat.innerHTML+=`<div class=\\"msg bot\\">${{d.reply}}</div>`; chat.scrollTop=chat.scrollHeight;
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
