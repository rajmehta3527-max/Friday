from flask import Flask, request, jsonify
import requests, re, time
from urllib.parse import quote

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FRIDAY - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box} body{margin:0;background:#F6F3EE;color:#1A1A1A;font-family:'Inter',sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden}
.header{padding:14px 20px;background:#fff;border-bottom:1px solid #E8E2D9;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:16px}.header span{font-size:10px;border:1px solid #E8E2D9;padding:4px 10px;border-radius:100px;color:#8C857B}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:14px;line-height:1.7;font-size:14px;white-space:pre-wrap;word-wrap:break-word}
.user{align-self:flex-end;background:#1A1A1A;color:#fff;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#fff;border:1px solid #E8E2D9;font-family:'Libre Baskerville',serif;border-bottom-left-radius:4px}
.footer{padding:12px 16px;background:#fff;border-top:1px solid #E8E2D9;display:flex;gap:8px}
input{flex:1;background:#F6F3EE;border:1px solid #E8E2D9;padding:12px 16px;border-radius:100px;outline:none;font-family:'Inter'}
button{border:none;background:#1A1A1A;color:#fff;padding:12px 20px;border-radius:100px;font-weight:600;cursor:pointer}
.credit{text-align:center;font-size:10px;color:#8C857B;padding:6px}
</style>
</head>
<body>
<div class="header"><h2>FRIDAY</h2><span>BY RAJ MEHTA</span></div>
<div id="chat"><div class="msg bot">Hi, I am Friday by Raj Mehta. Ask me anything - I will answer fast.</div></div>
<div class="footer"><input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button></div>
<div class="credit">Made by <b>Raj Mehta</b> @rajmehta_087</div>
<script>
const chat=document.getElementById('chat');
function add(t,c){ const d=document.createElement('div'); d.className='msg '+c; d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return; add(m,'user'); i.value='';
 let l=add('...','bot');
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  let j=await r.json(); l.innerText=j.reply;
 }catch{ l.innerText='Error, try again'; }
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body>
</html>
"""

# --- DEV INFO ---
DEV_INFO = """I am FRIDAY, created by Raj Mehta.

👨‍💻 Developer: Raj Mehta
🎂 Age: 18 years old
📸 Instagram: @rajmehta_087

Raj is a young developer from India who built me as his personal AI assistant. He loves coding, AI, and building cool projects."""

def is_about_dev(query):
    q = query.lower()
    keywords = ["who made you", "who created you", "your developer", "your dev", "who is your dev",
                "about dev", "about developer", "who is raj", "who is raj mehta",
                "your name", "your owner", "kisne banaya", "tumhe kisne banaya",
                "tumhara naam", "who are you", "tell about yourself", "your creator"]
    return any(k in q for k in keywords)

def get_answer(msg):
    urls = [
        f"https://text.pollinations.ai/{quote(msg)}?model=openai",
        f"https://text.pollinations.ai/{quote(msg)}?model=mistral",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.text) > 20:
                return r.text
        except:
            continue
    try:
        r = requests.post("https://text.pollinations.ai/openai",
            json={"model":"openai","messages":[{"role":"system","content":"You are FRIDAY created by Raj Mehta, 18, Insta @rajmehta_087. Answer helpfully."},{"role":"user","content":msg}],"stream":False}, timeout=12)
        if r.status_code==200:
            return r.json()['choices'][0]['message']['content']
    except:
        pass
    return None

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat():
    m = request.json.get('message','')

    # 1. If asking about dev - reply instantly with your info
    if is_about_dev(m):
        return jsonify({"reply": DEV_INFO})

    time.sleep(0.3)
    ans = get_answer(m)

    if not ans:
        ans = f"I'm FRIDAY by Raj Mehta (18, @rajmehta_087). You asked about '{m}'. I'm facing a small server delay, please ask again in 2 seconds for detailed answer."

    ans = re.sub(r'\*\*','',ans)
    return jsonify({"reply": ans[:4000]})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
