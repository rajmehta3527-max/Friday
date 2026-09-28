from flask import Flask, request, jsonify, send_from_directory
from fpdf import FPDF
import os, uuid, requests, re, base64

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

# Copy your uploaded image to static for orb
try:
    import shutil
    shutil.copy("/mnt/data/wa_image_8307250199237860360", "static/orb.jpg")
except: pass

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FRIDAY - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#02060C;color:#C7E8FF;font-family:'Share Tech Mono',monospace;height:100vh;overflow:hidden;position:relative}
body::before{content:"";position:fixed;inset:0;background:radial-gradient(ellipse at center, rgba(0,212,255,0.08) 0%, transparent 70%), url('/static/orb.jpg');background-size:cover;background-position:center;opacity:0.25;z-index:-1}
.grid-bg{position:fixed;inset:0;background-image:linear-gradient(rgba(0,212,255,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.07) 1px, transparent 1px);background-size:40px 40px;z-index:-1;opacity:0.3}

.top-bar{margin:12px 16px;padding:14px 20px;border:1px solid rgba(0,212,255,0.4);background:linear-gradient(90deg, rgba(0,20,40,0.9), rgba(0,40,60,0.6));display:flex;justify-content:space-between;align-items:center;clip-path:polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px));box-shadow:0 0 30px rgba(0,212,255,0.2)}
.top-bar h1{font-family:'Orbitron';color:#5EE7FF;font-size:36px;letter-spacing:2px;text-shadow:0 0 20px #00D4FF;line-height:1}
.top-bar h1 span{font-size:13px;display:block;color:#9FDFFF;letter-spacing:1px;font-family:'Share Tech Mono'}
.online{color:#8AFF8A;font-size:13px;text-align:right}
.online b{color:#fff}

.main{display:grid;grid-template-columns:280px 1fr 380px;gap:16px;padding:0 16px;height:calc(100vh - 140px)}

.panel{background:rgba(5,15,30,0.85);border:1px solid rgba(0,212,255,0.25);backdrop-filter:blur(12px);padding:16px;position:relative;clip-path:polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);box-shadow:0 0 20px rgba(0,212,255,0.15) inset}
.panel-title{font-family:'Orbitron';color:#5EE7FF;font-size:16px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.bar{margin:12px 0}
.bar-top{display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px}
.progress{height:4px;background:rgba(255,255,255,0.1);position:relative}
.progress span{display:block;height:100%;background:linear-gradient(90deg,#FFB86A,#FF8C00);box-shadow:0 0 8px #FF8C00}
.green{color:#5EFF8A}

.center{position:relative;display:flex;justify-content:center;align-items:center}
.orb-wrap{width:520px;height:520px;border-radius:50%;position:relative;background:radial-gradient(circle, rgba(0,212,255,0.15) 0%, transparent 70%);display:flex;justify-content:center;align-items:center;animation:spin 60s linear infinite}
.orb-wrap::before{content:"";position:absolute;inset:-20px;border:1px dashed rgba(0,212,255,0.3);border-radius:50%;animation:spin 20s linear infinite reverse}
.orb-wrap::after{content:"";position:absolute;inset:-40px;border:1px solid rgba(255,140,0,0.2);border-radius:50%}
.orb-img{width:92%;height:92%;border-radius:50%;background:url('/static/orb.jpg');background-size:160%;background-position:center;box-shadow:0 0 80px rgba(0,212,255,0.6), 0 0 120px rgba(255,140,0,0.4);animation:float 4s ease-in-out infinite}
@keyframes spin{to{transform:rotate(360deg)}} @keyframes float{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}

.chat-panel{display:flex;flex-direction:column}
.chat-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;font-family:'Orbitron';color:#FFC77A}
#chatBox{flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:12px;max-height:calc(100% - 90px);padding-right:4px}
.msg{padding:10px 14px;border-radius:12px;font-size:12.5px;line-height:1.5;max-width:90%}
.user{align-self:flex-end;background:rgba(124,77,255,0.25);border:1px solid rgba(124,77,255,0.4);color:#fff}
.bot{align-self:flex-start;background:rgba(0,212,255,0.12);border:1px solid rgba(0,212,255,0.3);color:#C7E8FF;box-shadow:0 0 15px rgba(0,212,255,0.2)}
.bot img{width:100%;border-radius:8px;margin-top:8px;border:1px solid rgba(0,212,255,0.3)}
.bot video{width:100%;border-radius:8px;margin-top:8px}
.chat-input{display:flex;gap:8px;margin-top:10px;background:rgba(0,0,0,0.5);border:1px solid rgba(255,140,0,0.3);padding:8px;border-radius:8px}
.chat-input input{flex:1;background:transparent;border:none;color:#FFC77A;outline:none;font-family:'Share Tech Mono';font-size:13px}
.chat-input button{background:linear-gradient(90deg,#FF8C00,#FFB86A);border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-weight:bold}

.bottom{margin:12px 16px;padding:10px 20px;border:1px solid rgba(255,255,255,0.1);background:rgba(5,15,30,0.8);display:flex;justify-content:center;gap:20px;align-items:center;clip-path:polygon(10px 0, calc(100% - 10px) 0, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0 calc(100% - 10px), 0 10px)}
.bbtn{padding:6px 18px;border-radius:20px;border:1px solid rgba(0,212,255,0.4);background:rgba(0,212,255,0.1);color:#5EE7FF;font-family:'Orbitron';font-size:11px;cursor:pointer;transition:0.2s}
.bbtn:hover{background:rgba(0,212,255,0.25);box-shadow:0 0 15px #00D4FF}
.bbtn.orange{border-color:rgba(255,140,0,0.5);color:#FFC77A;background:rgba(255,140,0,0.15)}
.credit{font-size:9px;color:rgba(255,255,255,0.4);letter-spacing:1px;text-align:center;margin-top:6px;width:100%}
.credit b{color:#5EE7FF}.credit a{color:#FFC77A;text-decoration:none}

@media(max-width:1100px){.main{grid-template-columns:1fr;overflow-y:auto}.center{order:-1}.orb-wrap{width:340px;height:340px}body{overflow:auto;height:auto}}
</style>
</head>
<body>
<div class="grid-bg"></div>
<div class="top-bar">
<div><h1>FRIDAY<span>AI ASSISTANT • Made by Raj Mehta</span></h1></div>
<div class="online">● ONLINE • SECURE CONNECTION<br><span id="time">2024.12.19 • 22:14:03 UTC</span></div>
</div>

<div class="main">
<div class="panel">
<div class="panel-title">◧ SYSTEM STATUS</div>
<div class="bar"><div class="bar-top"><span>🟢 NEURAL NET:<br><span class="green">ACTIVE</span></span><span>98%</span></div><div class="progress"><span style="width:98%"></span></div></div>
<div class="bar"><div class="bar-top"><span>🛡️ POWER CORE:</span><span>94%</span></div><div class="progress"><span style="width:94%"></span></div></div>
<div class="bar"><div class="bar-top"><span>🔒 SECURITY:<br><span style="color:#5EE7FF">SECURE</span></span><span></span></div></div>
<div class="bar"><div class="bar-top"><span>⚡ LATENCY:<br>12ms</span></div></div>
<div class="bar" style="margin-top:20px;font-size:11px;line-height:1.6"><span>MODULES:</span><br>[NLP ACTIVE]<br>[RECOGNITION ONLINE]<br>[THREAT SCAN: CLEAR]</div>
</div>

<div class="center"><div class="orb-wrap"><div class="orb-img"></div></div></div>

<div class="panel chat-panel">
<div class="chat-head"><span>☰ CHAT</span><span style="cursor:pointer" onclick="document.getElementById('chatBox').innerHTML=''">X</span></div>
<div id="chatBox">
<div class="msg bot"><b>You:</b><br>Initialize diagnostic protocol.<br><small>22:13:51</small></div>
<div class="msg bot"><b>FRIDAY:</b><br>Diagnostics complete. All systems nominal. Ready to assist. How can I help you today?<br><small>22:14:00</small></div>
</div>
<div class="chat-input"><input id="userInput" placeholder="Type your message..."><button onclick="sendMessage()">➤</button></div>
<div style="display:flex;gap:6px;margin-top:8px;flex-wrap:wrap">
<button class="bbtn" onclick="generateImage()">IMAGE</button>
<button class="bbtn" onclick="generateVideo()">VIDEO</button>
<button class="bbtn orange" onclick="startMic()">🎤 VOICE</button>
</div>
</div>
</div>

<div class="bottom">
<button class="bbtn" onclick="startMic()">[ VOICE ]</button>
<button class="bbtn orange" onclick="generateImage()">[ DIAGNOSE ]</button>
<button class="bbtn">[ HISTORY ]</button>
</div>
<div class="credit">FRIDAY v3.1 • AI ENGINE • SECURE ENCRYPTION • Made by <b>RAJ MEHTA</b> • <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>

<script>
const chatBox=document.getElementById('chatBox');
function addMsg(t,type){
  const d=document.createElement('div'); d.className='msg '+type;
  d.innerHTML=t; chatBox.appendChild(d); chatBox.scrollTop=chatBox.scrollHeight; return d;
}
async function sendMessage(){
  let inp=document.getElementById('userInput'); let m=inp.value.trim(); if(!m) return;
  addMsg(`<b>You:</b><br>${m}<br><small>${new Date().toLocaleTimeString()}</small>`,'user'); inp.value="";
  const load=addMsg('<b>FRIDAY:</b><br>Processing...','bot');
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    let j=await r.json(); load.remove();
    addMsg(`<b>FRIDAY:</b><br>${j.reply}<br><small>${new Date().toLocaleTimeString()}</small>`,'bot');
  }catch{ load.innerHTML='<b>FRIDAY:</b><br>Error, retry.'; }
}
async function generateImage(){
  let p=document.getElementById('userInput').value.trim()||prompt("Image prompt?");
  if(!p) return; addMsg(`<b>You:</b><br>${p}`,'user');
  const l=addMsg('<b>FRIDAY:</b><br>Generating image...','bot');
  let r=await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p, style:"cinematic, 3d render"})});
  let d=await r.json(); l.remove();
  addMsg(`<b>FRIDAY:</b><br><img src="${d.image_url}"><br><a href="${d.image_url}" target="_blank" style="color:#5EE7FF">Download HD - No Watermark</a>`,'bot');
}
async function generateVideo(){
  let p=document.getElementById('userInput').value.trim()||prompt("Video prompt?");
  if(!p) return; addMsg(`<b>You:</b><br>${p}`,'user');
  const l=addMsg('<b>FRIDAY:</b><br>Rendering video...','bot');
  let r=await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p})});
  let d=await r.json(); l.remove();
  addMsg(`<b>FRIDAY:</b><br><video src="${d.video_url}" controls autoplay loop muted playsinline></video><br><a href="${d.video_url}" target="_blank" style="color:#FFC77A">Download Video</a>`,'bot');
}
function startMic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR) return alert("Use Chrome"); const rec=new SR(); rec.lang='en-IN';
  rec.onresult=e=>{ document.getElementById('userInput').value=e.results[0][0].transcript; sendMessage(); }; rec.start();
}
document.getElementById('userInput').addEventListener('keypress',e=>{ if(e.key==='Enter') sendMessage(); });
setInterval(()=>{ document.getElementById('time').innerText=new Date().toISOString().replace('T',' • ').slice(0,19)+' UTC'; },1000);
</script>
</body>
</html>
"""

def get_ai(user_msg):
    try:
        r=requests.post("https://text.pollinations.ai/openai", json={"model":"openai","messages":[{"role":"system","content":"You are FRIDAY AI, made by Raj Mehta. Answer like JARVIS, cool, concise."},{"role":"user","content":user_msg}],"stream":False}, timeout=25)
        if r.status_code==200: return r.json()['choices'][0]['message']['content']
    except: pass
    try:
        r=requests.get(f"https://text.pollinations.ai/{requests.utils.quote(user_msg)}?model=openai", timeout=15)
        if r.status_code==200: return r.text
    except: pass
    return f"Systems nominal. Regarding '{user_msg}': Processing complete. I am FRIDAY by Raj Mehta."

@app.route('/')
def home(): return HTML_PAGE
@app.route('/chat', methods=['POST'])
def chat():
    msg=request.json.get('message',''); ans=get_ai(msg); ans=re.sub(r'\*\*(.*?)\*\*', r'\1', ans); return jsonify({"reply": ans[:3500]})
@app.route('/generate-image', methods=['POST'])
def gen_img():
    p=request.json.get('prompt',''); s=request.json.get('style','cinematic'); full=f"{p}, {s}, ultra detailed, no watermark"; safe=requests.utils.quote(full)
    url=f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&model=flux&enhance=true&nologo=true&seed={uuid.uuid4().hex[:5]}"
    return jsonify({"image_url": url})
@app.route('/generate-video', methods=['POST'])
def gen_vid():
    p=request.json.get('prompt',''); safe=requests.utils.quote(p); url=f"https://image.pollinations.ai/prompt/{safe}?model=turbo&video=true&nologo=true&enhance=true&seed={uuid.uuid4().hex[:4]}"
    return jsonify({"video_url": url})
@app.route('/static/<path:f>')
def static_f(f): return send_from_directory('static', f)

if __name__=='__main__':
    port=int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0', port=port)
