from flask import Flask, request, jsonify
import requests, re, os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>LIA - by Raj Mehta</title>
<style>
*{box-sizing:border-box}
html{height:100%;height:100dvh}
body{
  margin:0;padding:0;
  height:100%;height:100dvh;
  background:#FDF8F6;
  font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  display:flex;flex-direction:column;
  overflow:hidden;
}
.header{
  height:56px;flex-shrink:0;
  padding:0 16px;
  background:#fff;border-bottom:1px solid #eee;
  display:flex;justify-content:space-between;align-items:center;
}
.header h2{margin:0;font-family:serif;font-size:20px;letter-spacing:1px}
.header span{font-size:11px;border:1px solid #eee;padding:6px 12px;border-radius:20px;color:#999}

#chat{
  flex:1;
  overflow-y:auto;
  padding:16px;
  padding-bottom:90px; /* footer ke liye jagah */
  display:flex;flex-direction:column;gap:12px;
}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;font-size:15px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.user{align-self:flex-end;background:#111;color:#fff;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#fff;border:1px solid #eee;border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,0.05)}

/* Yehi main fix hai - phone ke liye */
.footer{
  position:fixed!important;
  bottom:0;left:0;right:0;
  height:75px;
  background:#fff;
  border-top:1px solid #eee;
  display:flex;align-items:center;gap:8px;
  padding:10px 12px;
  padding-bottom:calc(10px + env(safe-area-inset-bottom));
  z-index:9999;
}
.footer input{
  flex:1;height:48px;
  background:#f5f3f0;border:1.5px solid #e5ddd5;
  border-radius:24px;
  padding:0 18px;
  font-size:16px; /* iPhone zoom rokne ke liye 16px zaroori hai */
  outline:none;
}
.footer button{
  height:48px;min-width:70px;
  background:#111;color:#fff;
  border:none;border-radius:24px;
  font-weight:600;font-size:15px;
}
</style>
</head>
<body>
<div class="header"><h2>LIA</h2><span>BY RAJ MEHTA</span></div>
<div id="chat"><div class="msg bot">Hey! I'm LIA by Raj Mehta (18, @rajmehta_087). Ask me anything ✨</div></div>

<div class="footer">
  <input id="inp" type="text" placeholder="Type a message..." autocomplete="off" />
  <button onclick="send()">Send</button>
</div>

<script>
const chat=document.getElementById('chat');
function add(t,c){ const d=document.createElement('div'); d.className='msg '+c; d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return;
 add(m,'user'); i.value='';
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

DEV_INFO = "I am LIA, created by Raj Mehta. Age 18, Instagram @rajmehta_087"

def is_about_dev(q): return any(k in q.lower() for k in ["who made you","your developer","who is raj","your name"])

def get_lia_answer(prompt):
    if not GROQ_API_KEY: return "GROQ_API_KEY not set"
    MODELS = ["llama-3.3-70b-versatile","llama3-8b-8192","gemma2-9b-it","openai/gpt-oss-20b"]
    for model in MODELS:
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model":model,"messages":[{"role":"system","content":"You are LIA by Raj Mehta. Name is LIA only."},{"role":"user","content":prompt}]},
                timeout=25)
            if r.status_code==200: return r.json()['choices'][0]['message']['content']
        except: continue
    return "Groq failed, check console.groq.com/keys"

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m=request.json.get('message','').strip()
    if is_about_dev(m): return jsonify({"reply":DEV_INFO})
    return jsonify({"reply": re.sub(r'\*\*','',get_lia_answer(m))[:5000]})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
