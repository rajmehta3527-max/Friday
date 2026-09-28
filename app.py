from flask import Flask, request, jsonify
import re, random, datetime

MY_NAME = "Raj Mehta"
app = Flask(__name__)

# --- LOCAL SMART BRAIN ---
KNOWLEDGE = {
    "hustle": "MTV Hustle is Indian rap reality show on JioHotstar. Judges - Badshah, EPR, Ikka etc. Winner changes every season, latest is Season 4 winner was Lashcurry.",
    "legacy rap": "Legacy Rap Show is a podcast about hip-hop stories, not a competition, so it has no winner. It's interviews with rappers/producers.",
    "python": "Python is easiest coding language. Used for web (Django/Flask), AI, automation. Syntax looks like English, perfect for beginners.",
    "ethical hacking": "Learn networking -> Linux -> Python -> TryHackMe/HackTheBox labs. Always take permission, that's what makes it 'ethical'.",
    "raj mehta": f"{MY_NAME} - Class 12 Commerce from Chandigarh, hobby is Roasting. Made Friday AI.",
    "friday": f"I am Friday, made by {MY_NAME}. I'm offline version, but I remember your last chats!"
}

chat_history = []

def smart_offline_reply(user_msg):
    global chat_history
    msg = user_msg.lower().strip()
    chat_history.append(user_msg)
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    # 1. Creator check
    if any(x in msg for x in ["who made you", "kisne banaya", "developer", "who is raj", "about you"]):
        return f"hey I'm friday an AI assistant made by {MY_NAME}! {MY_NAME} is Class 12 Commerce, Chandigarh - Pro Roaster 🔥"

    # 2. Follow-up memory (this / uska winner)
    if "winner" in msg and ("this" in msg or "us" in msg or "iska" in msg):
        last_topic = " ".join(chat_history[-3:]).lower()
        if "legacy" in last_topic:
            return "Legacy Rap Show ka koi winner nahi hota bro, wo podcast hai interview wala, competition nahi. Tu shayad MTV Hustle puch raha hai?"
        if "hustle" in last_topic:
            return "Hustle ka winner har season alag hota hai. Season 4 ka Lashcurry tha. Tu kaunsa season puch raha hai?"

    # 3. Knowledge base search
    for key, ans in KNOWLEDGE.items():
        if key in msg:
            return ans

    # 4. Smart generic replies
    if "hello" in msg or "hi" in msg:
        return f"hey! I'm Friday offline wala, made by {MY_NAME}. Bolo kya help chahiye?"
    if "time" in msg:
        return f"Abhi time hai {datetime.datetime.now().strftime('%I:%M %p')}"
    
    # 5. Fallback - roasting style
    replies = [
        f"Ye topic mere offline brain me abhi nahi hai, but {MY_NAME} ne bola tha ispe kaam karne ko. Kuch aur pucho - python, hustle, hacking?",
        f"Offline hu isliye live search nahi kar pa raha, but pichla topic yaad hai: '{chat_history[-2] if len(chat_history)>1 else 'kuch nahi'}'. Uske baare me detail pucho.",
        "Samajh gaya! Offline version me main limited hu, but memory se kaam chala raha hu. Thoda specific pucho toh better jawab dunga."
    ]
    return random.choice(replies)

@app.route("/")
def home():
    return f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Friday Offline - by {MY_NAME}</title>
<style>
body{{margin:0;background:#121212;color:#eee;font-family:Arial;display:flex;flex-direction:column;height:100vh;}}
.header{{padding:14px;background:#1f1f1f;border-bottom:1px solid #333;font-weight:bold;display:flex;justify-content:space-between;}}
#chat{{flex:1;overflow:auto;padding:20px;display:flex;flex-direction:column;gap:14px;}}
.row{{max-width:80%;display:flex;flex-direction:column;}}.user{{align-self:flex-end;}}.bot{{align-self:flex-start;}}
.label{{font-size:10px;color:#888;margin-bottom:4px;}}.bubble{{padding:12px 16px;border-radius:18px;}}
.user .bubble{{background:#2b8cff;color:white;border-bottom-right-radius:4px;}}.bot .bubble{{background:#2a2a2a;border:1px solid #333;border-bottom-left-radius:4px;}}
.footer{{display:flex;padding:12px;background:#1f1f1f;gap:8px;}}input{{flex:1;padding:14px;border-radius:25px;border:1px solid #444;background:#2a2a2a;color:white;}}button{{padding:12px 18px;border-radius:25px;border:none;background:#2b8cff;color:white;font-weight:bold;}}
.offline{{font-size:10px;background:#ff9800;color:black;padding:3px 8px;border-radius:10px;}}
</style></head>
<body><div class="header"><span>Friday OFFLINE 🤖 <span class="offline">NO INTERNET NEEDED</span></span></div>
<div id="chat"><div class="row bot"><div class="label">FRIDAY</div><div class="bubble">hey I'm friday offline version made by {MY_NAME} - ab memory ke saath!</div></div></div>
<div class="footer"><input id="inp" placeholder="Ask offline..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>
async function send(){{
 let i=document.getElementById('inp'), t=i.value.trim(); if(!t)return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="row user"><div class="label">YOU</div><div class="bubble">${{t}}</div></div>`; i.value='';
 let r=await fetch('/chat',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:t}})}});
 let d=await r.json(); c.innerHTML+=`<div class="row bot"><div class="label">FRIDAY</div><div class="bubble">${{d.reply}}</div></div>`; c.scrollTop=c.scrollHeight;
}}
</script></body></html>
"""
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.get_json().get("message","")
    return jsonify({"reply": smart_offline_reply(msg)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
