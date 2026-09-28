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
body{margin:0;background:radial-gradient(circle at top, #1a2a5e, #0a0a0a);color:#fff;min-height:100vh;padding-bottom:80px}
.header{padding:18px 20px;background:rgba(255,255,255,0.06);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}
.header h2{margin:0;font-size:18px}
.badge{background:#2a5bd7;padding:4px 10px;border-radius:20px;font-size:12px}
#chatBox{height:60vh;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 14px;border-radius:18px;line-height:1.4;font-size:14px;animation:pop.2s}
@keyframes pop{from{transform:scale(.95);opacity:0}to{transform:scale(1);opacity:1}}
.user{align-self:flex-end;background:linear-gradient(135deg,#4a7bff,#2a5bd7);border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:rgba(255,255,255,0.09);border:1px solid rgba(255,255,255,0.1);border-bottom-left-radius:4px}
.bot img,.bot video{width:100%;border-radius:12px;margin-top:8px;border:1px solid rgba(255,255,255,0.15)}
.footer{padding:12px;background:rgba(0,0,0,0.6);backdrop-filter:blur(12px);position:fixed;bottom:0;width:100%;border-top:1px solid rgba(255,255,255,0.1)}
.input-row{display:flex;gap:8px}
#userInput{flex:1;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);color:#fff;padding:12px 15px;border-radius:25px;outline:none}
#style{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);color:#fff;padding:8px 12px;border-radius:20px}
.btn{border:none;padding:10px 14px;border-radius:20px;font-weight:600;cursor:pointer;background:#222;color:#fff;border:1px solid rgba(255,255,255,0.15)}
.btn-primary{background:linear-gradient(135deg,#4a7bff,#2a5bd7);border:none}
.actions{display:flex;gap:6px;margin-top:8px;overflow-x:auto}
a.dl{display:inline-block;margin-top:8px;background:#fff;color:#000;padding:6px 12px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:600}
.credit{text-align:center;font-size:11px;color:rgba(255,255,255,0.6);margin-top:8px;letter-spacing:0.5px}
.credit b{color:#fff}
.credit a{color:#6ea8ff;text-decoration:none;font-weight:600}
</style>
</head>
<body>
<div class="header"><h2>🤖 FRIDAY AI PRO MAX</h2><span class="badge">PRO</span></div>
<div id="chatBox"><div class="msg bot">Hey boss 👋 Bolo kya banana hai?<br><br>Try: <i>"a beautiful Indian girl using phone, sitting in cafe"</i><br><br>Tip: Real photo ke liye <b>📸 Realistic</b> select karo.</div></div>
<div class="footer">
<div class="input-row">
<input id="userInput" placeholder="Kuch bhi likho...">
<button class="btn btn-primary" onclick="sendMessage()">➤</button>
</div>
<div class="actions">
<select id="style">
<option value="realistic">📸 Realistic</option>
<option value="cinematic, ultra detailed portrait">🎬 Cinematic</option>
<option value="anime">🎨 Anime</option>
<option value="3d render">🧊 3D</option>
<option value="logo design, vector">💎 Logo</option>
<option value="poster art">🖼️ Poster</option>
</select>
<button class="btn btn-primary" onclick="generateImage()">🖼️ Image</button>
<button class="btn" onclick="generateVideo()">🎬 Video</button>
<button class="btn" onclick="startListening()">🎤</button>
<button class="btn" onclick="generateDoc()">📄 PDF</button>
</div>
<div class="credit">Made with ❤️ by <b>Raj Mehta</b> (Age 18) | Insta: <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>
</div>
<script>
const chatBox = document.getElementById('chatBox');
let lastBotReply = "";
function addMsg(text, type){ chatBox.innerHTML += `<div class="msg ${type}">${text}</div>`; chatBox.scrollTop = chatBox.scrollHeight; }
async function sendMessage(){
    let input = document.getElementById('userInput'); let msg = input.value; if(!msg) return;
    addMsg(msg, 'user'); input.value = "";
    let res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    let data = await res.json(); lastBotReply = data.reply; addMsg(data.reply, 'bot');
}
async function generateImage(){
    let prompt = document.getElementById('userInput').value; let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle likho!"); addMsg(`🖼️ ${prompt}`, 'user'); addMsg(`⏳ Image bana raha hu...`, 'bot');
    let res = await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json(); chatBox.lastChild.remove();
    addMsg(`${d.final_prompt}<br><img src="${d.image_url}"><br><a class="dl" href="${d.image_url}" target="_blank">⬇️ Download HD</a>`, 'bot');
}
async function generateVideo(){
    let prompt = document.getElementById('userInput').value; let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle kuch likho!"); addMsg(`🎬 Video: ${prompt}`, 'user'); addMsg(`⏳ Video render... 40 sec`, 'bot');
    let res = await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json(); chatBox.lastChild.remove();
    addMsg(`<b>${d.prompt}</b><br><video src="${d.video_url}" controls autoplay loop></video>`, 'bot');
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
    return jsonify({"reply": f"Samajh gaya: {msg} <br>Ab Image button dabao."})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt','').lower()
    style = request.json.get('style','realistic')
    enhanced = prompt
    if "girl" in prompt and "phone" in prompt:
        enhanced = f"{prompt}, beautiful girl holding smartphone in hand clearly, looking at phone screen, texting, natural light, detailed hands, 8k"
    elif "phone" in prompt:
        enhanced = f"{prompt}, holding smartphone clearly visible, using phone, detailed hands"
    full_prompt = f"{enhanced}, {style}, ultra detailed, sharp focus, highly detailed, photorealistic, 8k"
    safe_prompt = requests.utils.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1280&model=flux&enhance=true&nologo=true&seed={uuid.uuid4().hex[:6]}"
    return jsonify({"image_url": image_url, "final_prompt": f"Prompt: {full_prompt}"})

@app.route('/generate-video', methods=['POST'])
def generate_video():
    prompt = request.json.get('prompt','')
    style = request.json.get('style','cinematic')
    full_prompt = f"{prompt}, {style} video, smooth motion, 4k"
    safe_prompt = requests.utils.quote(full_prompt)
    video_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=video&nologo=true&enhance=true"
    return jsonify({"video_url": video_url, "prompt": full_prompt})

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text','')[:600]
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    path = os.path.join("static", filename)
    tts = gTTS(text=text, lang='en', tld='co.in')
    tts.save(path)
    return jsonify({"audio_url": f"/static/{filename}"})

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
