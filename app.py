from flask import Flask, request, jsonify
import requests, re

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
.msg{max-width:85%;padding:12px 16px;border-radius:14px;line-height:1.6;font-size:14px;white-space:pre-wrap;word-wrap:break-word}
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
  let j=await r.json(); l.remove(); add(j.reply,'bot');
 }catch{ l.innerText='Error, try again'; }
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body>
</html>
"""

def fast_ai(msg):
    # Fastest endpoint
    try:
        r = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(msg)}?model=openai&stream=false", timeout=10)
        if r.status_code==200 and len(r.text)>10:
            return r.text
    except: pass
    try:
        r = requests.post("https://text.pollinations.ai/openai", json={"model":"openai","messages":[{"role":"user","content":msg}],"stream":False}, timeout=15)
        if r.status_code==200:
            return r.json()['choices'][0]['message']['content']
    except: pass
    return "I'm FRIDAY by Raj Mehta. Please ask again, server was busy."

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat():
    m = request.json.get('message','')
    ans = fast_ai(m)
    ans = re.sub(r'\*\*','',ans)
    return jsonify({"reply": ans[:4000]})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
