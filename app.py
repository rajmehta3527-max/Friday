from flask import Flask, request, jsonify, send_from_directory
from fpdf import FPDF
import os, uuid, requests, re

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FRIDAY - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;background:#F6F3EE;color:#1A1A1A;font-family:'Inter',sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden}
.header{padding:14px 20px;background:#FFFFFF;border-bottom:1px solid #E8E2D9;display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:17px;letter-spacing:-0.5px}
.header span{font-size:10px;border:1px solid #E8E2D9;padding:4px 10px;border-radius:100px;color:#8C857B}
#chatBox{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:14px;scroll-behavior:smooth}
.msg{max-width:84%;padding:14px 16px;border-radius:14px;line-height:1.7;font-size:14px;word-wrap:break-word;white-space:pre-wrap}
.user{align-self:flex-end;background:#1A1A1A;color:#F6F3EE;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#FFFFFF;border:1px solid #E8E2D9;border-bottom-left-radius:4px;font-family:'Libre Baskerville',serif;color:#2B2B2B;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.bot img{width:100%;max-width:320px;border-radius:10px;margin-top:10px;display:block;border:1px solid #E8E2D9;cursor:zoom-in}
.bot video{width:100%;max-width:320px;border-radius:10px;margin-top:10px;background:#000}
.footer{padding:12px 16px;background:#FFFFFF;border-top:1px solid #E8E2D9;flex-shrink:0}
.input-row{display:flex;gap:8px;align-items:center}
#userInput{flex:1;background:#F6F3EE;border:1px solid #E8E2D9;padding:12px 16px;border-radius:100px;outline:none;font-family:'Inter',sans-serif}
.btn{border:1px solid #E8E2D9;background:#FFF;padding:9px 14px;border-radius:100px;font-weight:500;cursor:pointer;font-size:13px}
.btn-primary{background:#1A1A1A;color:#FFF;border-color:#1A1A1A}
.actions{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
a.dl{display:inline-block;margin-top:10px;background:#1A1A1A;color:#fff;padding:7px 14px;border-radius:100px;text-decoration:none;font-size:12px}
.credit{text-align:center;font-size:11px;color:#8C857B;margin-top:10px}
.credit b{color:#1A1A1A}.credit a{color:#1A1A1A;text-decoration:underline;font-weight:600}
#imgModal{display:none;position:fixed;inset:0;background:rgba(246,243,238,0.95);z-index:999;justify-content:center;align-items:center;padding:20px}
#imgModal img{max-width:95%;max-height:90%;border-radius:12px;box-shadow:0 10px 40px rgba(0,0,0,0.2)}
#imgModal span{position:absolute;top:18px;right:22px;font-size:28px;cursor:pointer;color:#1A1A1A}
</style>
</head>
<body>
<div class="header"><h2>FRIDAY — AI STUDIO</h2><span>MADE BY RAJ MEHTA</span></div>
<div id="chatBox"><div class="msg bot">Hello, I am Friday.

• Ask anything - I will answer properly
• Image generation - No watermark
• Video generation
• Voice input

Try: "Tell me about Jawa bikes"</div></div>
<div id="imgModal" onclick="this.style.display='none'"><span>×</span><img id="modalImg"></div>
<div class="footer">
<div class="input-row">
<input id="userInput" placeholder="Ask anything or image prompt...">
<button class="btn" onclick="startMic()" title="Mic">🎤</button>
<button class="btn btn-primary" onclick="sendMessage()">Send</button>
</div>
<div class="actions">
<select id="style" class="btn"><option value="realistic photorealistic">📸 Realistic</option><option value="cinematic">🎬 Cinematic</option><option value="anime">🎨 Anime</option><option value="minimal logo vector">💎 Logo</option></select>
<button class="btn btn-primary" onclick="generateImage()">🖼️ Image</button>
<button class="btn" onclick="generateVideo()">🎬 Video</button>
<button class="btn" onclick="generateDoc()">📄 PDF</button>
</div>
<div class="credit">Made with ❤️ by <b>Raj Mehta</b> (18) | Insta: <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>
</div>
<script>
const chatBox=document.getElementById('chatBox');
function scrollToBottom(){ chatBox.scrollTop=chatBox.scrollHeight; }
function addMsg(t,type){
  const d=document.createElement('div'); d.className='msg '+type;
  d.innerHTML=t;
  d.querySelectorAll('img').forEach(im=>{ im.onclick=()=>{ document.getElementById('modalImg').src=im.src; document.getElementById('imgModal').style.display='flex'; }});
  chatBox.appendChild(d); setTimeout(scrollToBottom,100); return d;
}
async function sendMessage(){
  let inp=document.getElementById('userInput'); let m=inp.value.trim(); if(!m) return;
  addMsg(m,'user'); inp.value=""; const load=addMsg('Thinking...','bot');
  try{
    let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    let j=await r.json(); load.remove(); addMsg(j.reply,'bot');
  }catch{ load.innerHTML='Error, try again'; }
}
async function generateImage(){
  let p=document.getElementById('userInput').value.trim(); let s=document.getElementById('style').value;
  if(!p) return alert("Prompt likho!"); addMsg(p,'user');
  const l=addMsg('Generating image (no watermark)...','bot');
  try{
    let r=await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p, style:s})});
    let d=await r.json(); l.remove();
    addMsg(`${d.final_prompt}<br><img src="${d.image_url}" onload="scrollToBottom()"><br><a class="dl" href="${d.image_url}" target="_blank">Download HD</a>`,'bot');
  }catch{ l.innerHTML='Image failed, try again'; }
}
async function generateVideo(){
  let p=document.getElementById('userInput').value.trim(); if(!p) return alert("Video prompt likho!");
  addMsg(p,'user'); const l=addMsg('Generating video... 30 sec wait','bot');
  try{
    let r=await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p})});
    let d=await r.json(); l.remove();
    addMsg(`<video src="${d.video_url}" controls autoplay loop muted playsinline onloadeddata="scrollToBottom()"></video><br><a class="dl" href="${d.video_url}" target="_blank">Download Video</a>`,'bot');
  }catch{ l.innerHTML='Video failed'; }
}
function startMic(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR) return alert("Mic ke liye Chrome use karo");
  const rec=new SR(); rec.lang='en-IN';
  rec.onstart=()=>{ document.getElementById('userInput').placeholder="Listening..."; };
  rec.onend=()=>{ document.getElementById('userInput').placeholder="Ask anything or image prompt..."; };
  rec.onresult=e=>{ document.getElementById('userInput').value=e.results[0][0].transcript; sendMessage(); };
  rec.start();
}
async function generateDoc(){
  let c=document.getElementById('userInput').value; if(!c) return alert("PDF text likho");
  let r=await fetch('/generate-doc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content:c})});
  let d=await r.json(); addMsg(`<a class="dl" href="${d.file_url}" download>Download PDF</a>`,'bot');
}
document.getElementById('userInput').addEventListener('keypress',e=>{ if(e.key==='Enter') sendMessage(); });
</script>
</body>
</html>
"""

def get_ai_answer(msg):
    try:
        # Main - POST method, most stable on Render
        r = requests.post("https://text.pollinations.ai/openai",
            json={"model":"openai","messages":[{"role":"system","content":"You are FRIDAY AI created by Raj Mehta (18, @rajmehta_087). Answer helpfully, concise, clean formatting, no **."},{"role":"user","content":msg}],"stream":False}, timeout=30)
        if r.status_code==200:
            return r.json()['choices'][0]['message']['content']
    except: pass
    try:
        r = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(msg)}?model=openai", timeout=20)
        if r.status_code==200 and len(r.text)>20: return r.text
    except: pass
    return None

@app.route('/')
def home(): return HTML_PAGE

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message','')
    ans = get_ai_answer(msg)
    if not ans:
        ans = f"I'm FRIDAY by Raj Mehta. You asked: '{msg}'. I can explain anything. For example - Jawa bikes are iconic retro motorcycles, now made in India by Classic Legends, 293cc engine, compete with Royal Enfield. Ask me more specifically!"
    ans = re.sub(r'\*\*(.*?)\*\*', r'\1', ans)
    return jsonify({"reply": ans[:4000]})

@app.route('/generate-image', methods=['POST'])
def gen_img():
    p = request.json.get('prompt',''); s = request.json.get('style','realistic')
    full = f"{p}, {s}, ultra detailed, sharp, no watermark, no logo, no text, clean"
    safe = requests.utils.quote(full)
    url = f"https://image.pollinations.ai/prompt/{safe}?width=1024&height=1024&model=flux&enhance=true&nologo=true&nofeed=true&private=true&seed={uuid.uuid4().hex[:6]}"
    return jsonify({"image_url": url, "final_prompt": full})

@app.route('/generate-video', methods=['POST'])
def gen_vid():
    p = request.json.get('prompt','')
    safe = requests.utils.quote(f"{p}, cinematic video, smooth motion, 4k")
    url = f"https://image.pollinations.ai/prompt/{safe}?model=turbo&video=true&nologo=true&enhance=true&seed={uuid.uuid4().hex[:4]}"
    return jsonify({"video_url": url})

@app.route('/generate-doc', methods=['POST'])
def gen_doc():
    c = request.json.get('content',''); fname = f"{uuid.uuid4().hex}.pdf"; path = os.path.join("static", fname)
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Times", size=12); pdf.multi_cell(0, 8, c); pdf.output(path)
    return jsonify({"file_url": f"/static/{fname}"})

@app.route('/static/<path:f>')
def static_f(f): return send_from_directory('static', f)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
