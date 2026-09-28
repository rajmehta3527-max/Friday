from flask import Flask, request, jsonify
import os, random

app = Flask(__name__)

# Simple brain - agar OpenAI key nahi hai to ye chalega
def get_friday_reply(message):
    message = message.lower()
    if "hello" in message or "hi" in message:
        return "Hello Boss! Friday here. How can I help you today? 🚀"
    if "kaun hai" in message or "who are you" in message:
        return "I'm Friday, your personal AI assistant made by you! Ask me anything."
    if "time" in message:
        return "I don't have real-time access right now, but I'm always here for you!"
    if "code" in message or "python" in message:
        return "Bilkul! Konsa code chahiye? Python, Flask, AI... batao mai bana deta hu."
    if "love" in message:
        return "Aww 🥺 Love you too Boss!"
    
    replies = [
        f"You said: '{message}'. Interesting! Batao ispe detail me kya karna hai?",
        "Samajh gaya! Friday is on it. Thoda aur batao iske baare me?",
        "Boss, ye to easy hai. Mai iska best solution deta hu - bolo kahan use karna hai?",
        "Nice question! As your Friday, I think we should do it smartly. What's your plan?"
    ]
    return random.choice(replies)

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friday AI</title>
<style>
body{margin:0; font-family:'Segoe UI',sans-serif; background:#0f0f0f; color:white; display:flex; flex-direction:column; height:100vh;}
.header{padding:15px; text-align:center; background:#1a1a1a; border-bottom:1px solid #333; font-size:20px; font-weight:bold;}
#chat{flex:1; overflow-y:auto; padding:20px; display:flex; flex-direction:column; gap:15px;}
.msg{max-width:80%; padding:12px 16px; border-radius:18px; line-height:1.4;}
.user{align-self:flex-end; background:#2b8cff; color:white; border-bottom-right-radius:4px;}
.bot{align-self:flex-start; background:#232323; border:1px solid #333; border-bottom-left-radius:4px;}
.footer{display:flex; padding:15px; background:#1a1a1a; gap:10px;}
#inp{flex:1; padding:14px 18px; border-radius:25px; border:1px solid #333; background:#232323; color:white; outline:none;}
#send{padding:12px 20px; border-radius:25px; border:none; background:#2b8cff; color:white; font-weight:bold; cursor:pointer;}
</style>
</head>
<body>
<div class="header">Friday AI 🤖</div>
<div id="chat"><div class="msg bot">Hey! I'm Friday. Your AI is finally LIVE! Puchho kuch bhi...</div></div>
<div class="footer">
<input id="inp" placeholder="Message Friday..." onkeypress="if(event.key==='Enter')send()">
<button id="send" onclick="send()">Send</button>
</div>
<script>
async function send(){
 let input = document.getElementById('inp');
 let text = input.value.trim();
 if(!text) return;
 let chat = document.getElementById('chat');
 chat.innerHTML += `<div class="msg user">${text}</div>`;
 input.value = '';
 chat.scrollTop = chat.scrollHeight;
 
 let res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text})});
 let data = await res.json();
 chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;
 chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    reply = get_friday_reply(user_msg)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
