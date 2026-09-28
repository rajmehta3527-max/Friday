from flask import Flask, request, jsonify
import os

MY_NAME = "Raj Mehta"
MY_CLASS = "Class 12 - Commerce"
MY_HOBBY = "Roasting"

app = Flask(__name__)

# Knowledge base - ab ye sab ka jawab dega
KNOWLEDGE = {
    "prime minister of india": "Prime Minister of India is Narendra Modi (since 2014). He is the 14th PM of India.",
    "pm of india": "Narendra Modi is the PM of India.",
    "president of india": "President of India is Droupadi Murmu.",
    "capital of india": "New Delhi is the capital of India.",
    "who is raj mehta": f"{MY_NAME} is a {MY_CLASS} student from Chandigarh. Hobby: {MY_HOBBY}. Creator of Friday AI!",
}

def get_friday_reply(message):
    msg = message.lower().strip()

    # 1. Check for dev info
    if any(x in msg for x in ["who is your dev", "who made you", "developer", "kisne banaya"]):
        return f"I'm Friday, developed by {MY_NAME}! {MY_CLASS}, Hobby: {MY_HOBBY} 🔥"

    # 2. Check knowledge base
    for key, ans in KNOWLEDGE.items():
        if key in msg:
            return ans

    # 3. Roasting mode
    if "roast" in msg:
        return "Yo, you want a roast? My boss Raj Mehta is the king of roasting! Tell me who to roast 😏🔥"

    # 4. Try Groq/OpenAI if key is added (optional)
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        try:
            import requests
            res = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "llama3-8b-8192", "messages": [{"role":"user","content": message}]}, timeout=10)
            return res.json()['choices'][0]['message']['content']
        except:
            pass

    return f"Good question: '{message}'. Currently I'm running on my basic brain. For PM of India - It's Narendra Modi. Tell me what you want to know, I have answers for many GK questions! And if you want me to be ChatGPT smart, add a free GROQ_API_KEY in Render."

@app.route("/")
def home():
    return f"""
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Friday by {MY_NAME}</title>
<style>
body{{margin:0; background:#0f0f0f; color:white; font-family:sans-serif; display:flex; flex-direction:column; height:100vh;}}
.header{{padding:15px; background:#1a1a1a; border-bottom:1px solid #333; display:flex; justify-content:space-between;}}
#chat{{flex:1; overflow:auto; padding:20px; display:flex; flex-direction:column; gap:12px;}}
.msg{{max-width:85%; padding:12px 16px; border-radius:18px;}}
.user{{align-self:flex-end; background:#2b8cff;}}.bot{{align-self:flex-start; background:#232323; border:1px solid #333;}}
.footer{{display:flex; padding:12px; background:#1a1a1a; gap:8px;}}
input{{flex:1; padding:14px; border-radius:25px; border:1px solid #333; background:#232323; color:white;}}
button{{padding:12px 18px; border-radius:25px; border:none; background:#2b8cff; color:white; font-weight:bold;}}
#about{{display:none; position:fixed; inset:0; background:rgba(0,0,0,0.8); justify-content:center; align-items:center;}}
.box{{background:#1e1e1e; padding:25px; border-radius:16px; text-align:center; border:1px solid #333; width:90%; max-width:380px;}}
</style></head><body>
<div class="header"><b>Friday AI 🤖 - by {MY_NAME}</b><a href="#" onclick="document.getElementById('about').style.display='flex';return false" style="color:#2b8cff; border:1px solid #2b8cff; padding:5px 12px; border-radius:20px; text-decoration:none; font-size:13px">About Me</a></div>
<div id="chat"><div class="msg bot">Hey I'm Friday v2! Now I know PM of India and more. Ask me anything - PM, President, Capital etc.</div></div>
<div class="footer"><input id="inp" placeholder="Ask e.g. PM of India..." onkeypress="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<div id="about" onclick="this.style.display='none'"><div class="box" onclick="event.stopPropagation()"><h2>👋 {MY_NAME}</h2><p>{MY_CLASS}</p><p>🔥 Hobby: {MY_HOBBY}</p><p style="color:#aaa; font-size:13px">Creator of Friday AI | Chandigarh</p><button onclick="document.getElementById('about').style.display='none'" style="background:#333; padding:8px 16px; border-radius:20px; border:none; color:white; margin-top:10px">Close</button></div></div>
<script>
async function send(){{
 let i=document.getElementById('inp'); let t=i.value.trim(); if(!t) return;
 let c=document.getElementById('chat'); c.innerHTML+=`<div class="msg user">${{t}}</div>`; i.value=''; c.scrollTop=c.scrollHeight;
 let r=await fetch('/chat',{{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{message:t}})}});
 let d=await r.json(); c.innerHTML+=`<div class="msg bot">${{d.reply}}</div>`; c.scrollTop=c.scrollHeight;
}}
</script></body></html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"reply": get_friday_reply(request.get_json().get("message",""))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
