from flask import Flask, request, jsonify, send_from_directory
from gtts import gTTS
from fpdf import FPDF
import os, uuid, requests

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friday AI PRO MAX - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{font-family:'Outfit',sans-serif;box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top, #1a2a5e, #0a0a0a);color:#fff;min-height:100vh}
.header{padding:15px 20px;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}
#chatBox{height:calc(100vh - 140px);overflow-y:auto;padding:15px 15px 20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 14px;border-radius:18px;line-height:1.4;font-size:14px}
.user{align-self:flex-end;background:linear-gradient(135deg,#4a7bff,#2a5bd7);border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:rgba(255,255,255,0.09);border:1px solid rgba(255,255,255,0.1);border-bottom-left-radius:4px;width:fit-content;max-width:90%}
.bot img{max-width:320px;max-height:45vh;object-fit:contain;border-radius:12px;margin-top:8px;cursor:zoom-in;border:1px solid rgba(255,255,255,0.2);display:block}
.bot img:hover{transform:scale(1.02);transition:.2s}
.bot video{max-width:320px;border-radius:12px;margin-top:8px}
.footer{padding:12px;background:rgba(0,0,0,0.7);backdrop-filter:blur(12px);position:fixed;bottom:0;width:100%;border-top:1px solid rgba(255,255,255,0.1);z-index:10}
.input-row{display:flex;gap:8px}
#userInput{flex:1;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);color:#fff;padding:12px 15px;border-radius:25px;outline:none}
.btn{border:none;padding:9px 13px;border-radius:20px;font-weight:600;cursor:pointer;background:#222;color:#fff;border:1px solid rgba(255,255,255,0.15);font-size:13px}
.btn-primary{background:linear-gradient(135deg,#4a7bff,#2a5bd7);border:none}
.actions{display:flex;gap:6px;margin-top:8px}
a.dl{display:inline-block;margin-top:8px;background:#fff;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:600}
.credit{text-align:center;font-size:11px;color:rgba(255,255,255,0.6);margin-top:8px}
.credit b{color:#fff} .credit a{color:#6ea8ff;text-decoration:none}
#imgModal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);z-index:999;justify-content:center;align-items:center;padding:20px}
#imgModal img{max-width:95%;max-height:90%;border-radius:12px;object-fit:contain}
#imgModal span{position:absolute;top:15px;right:20px;font-size:30px;cursor:pointer}
</style>
</head>
<body>
<div class="header"><h2>🤖 FRIDAY AI PRO MAX</h2><span style="background:#2a5bd7;padding:4px 10px;border-radius:20px;font-size:12px">PRO</span></div>
<div id="chatBox"><div class="msg bot">Hey boss 👋 <br>Try: <i>"a girl playing with cat"</i> <br>Image pe click karke full dekho - No watermark!</div></div>
<div id="imgModal" onclick="this.style.display='none'"><span>×</span><img id="modalImg"></div>
<div class="footer">
<div class="input-row"><input id="userInput" placeholder="Kuch bhi likho..."><button class="btn btn-primary" onclick="sendMessage()">➤</button></div>
<div class="actions">
<select id="style" class="btn"><option value="realistic">📸 Realistic</option><option value="cinematic">🎬 Cinematic</option><option value="anime">🎨 Anime</option><option value="3d render">🧊 3D</option><option value="logo design">💎 Logo</option></select>
<button class="btn btn-primary" onclick="generateImage()">🖼️ Image</button>
<button class="btn" onclick="generateVideo()">🎬 Video</button>
<button class="btn" onclick="startListening()">🎤</button>
<button class="btn" onclick="generateDoc()">📄 PDF</button>
</div>
<div class="credit">Made with ❤️ by <b>Raj Mehta</b> (18) | Insta: <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>
</div>
<script>
const chatBox = document.getElementById('chatBox');
function addMsg(text, type){ 
  const div = document.createElement('div'); div.className='msg '+type; div.innerHTML=text;
  div.querySelectorAll('img').forEach(img=>{ img.onclick=()=>{ document.getElementById('modalImg').src=img.src; document.getElementById('imgModal').style.display='flex'; } });
  chatBox.appendChild(div); chatBox.scrollTop = chatBox.scrollHeight; 
}
async function sendMessage(){
    let input = document.getElementById('userInput'); let msg = input.value; if(!msg) return;
    addMsg(msg, 'user'); input.value = "";
    let res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    let data = await res.json(); addMsg(data.reply, 'bot');
}
async function generateImage(){
    let prompt = document.getElementById('userInput').value; let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle likho!"); 
    addMsg(prompt, 'user'); 
    const loadingId = Date.now(); addMsg(`<span id="${loadingId}">⏳ Generating... 5 sec</span>`, 'bot');
    let res = await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json(); 
    document.getElementById(loadingId).parentElement.remove();
    addMsg(`${d.final_prompt}<br><img src="${d.image_url}"><br><a class="dl" href="${d.image_url}" target="_blank">⬇️ Download HD (No Watermark)</a>`, 'bot');
}
async function generateVideo(){
    let prompt = document.getElementById('userInput').value; let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle likho!"); addMsg(prompt, 'user'); addMsg(`⏳ Video 40 sec...`, 'bot');
    let res = await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json(); chatBox.lastChild.remove();
    addMsg(`<video src="${d.video_url}" controls autoplay loop></video>`, 'bot');
}
function startListening(){ const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)(); rec.lang = 'en-IN'; rec.start(); rec.onresult = e => { document.getElementById('userInput').value = e.results[0][0].transcript; } }
async function generateDoc(){
    let content = document.getElementById('userInput').value; if(!content) return alert("PDF me kya likhna hai wo likho");
    let res = await fetch('/generate-doc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content})});
    let d = await res.json(); addMsg(`<a class="dl" href="${d.file_url}" download>📄 Download PDF</a>`, 'bot');
}
document.getElementById('userInput').addEventListener('keypress', e=>{ if(e.key==='Enter') sendMessage(); });
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML_PAGE

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message','')
    return jsonify({"reply": f"Samajh gaya: {msg}. Image button dabao!"})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt','').lower()
    style = request.json.get('style','realistic')
    
    enhanced = prompt
    if "girl" in prompt and "cat" in prompt:
        enhanced = f"{prompt}, beautiful girl holding cute cat, cuddling cat, cat clearly visible"
    elif "girl" in prompt and "phone" in prompt:
        enhanced = f"{prompt}, holding smartphone clearly in hand, looking at screen"

    # NO WATERMARK FIX
    full_prompt = f"{enhanced}, {style}, ultra detailed, sharp focus, photorealistic, 8k, no watermark, no logo, no text, clean image"
    safe_prompt = requests.utils.quote(full_prompt)
    
    # nologo=true + nofeed=true + private=true = no watermark
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=768&height=1024&model=flux&enhance=true&nologo=true&nofeed=true&private=true&seed={uuid.uuid4().hex[:6]}"
    
    return jsonify({"image_url": image_url, "final_prompt": f"Prompt: {full_prompt}"})

@app.route('/generate-video', methods=['POST'])
def generate_video():
    prompt = request.json.get('prompt','')
    style = request.json.get('style','cinematic')
    safe_prompt = requests.utils.quote(f"{prompt}, {style} video, 4k, no watermark")
    video_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=video&nologo=true&nofeed=true&private=true"
    return jsonify({"video_url": video_url, "prompt": prompt})

@app.route('/generate-doc', methods=['POST'])
def generate_doc():
    content = request.json.get('content','')
    filename = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join("static", filename)
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12); pdf.multi_cell(0, 10, content); pdf.output(path)
    return jsonify({"file_url": f"/static/{filename}"})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
