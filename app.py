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
<title>Friday AI PRO MAX</title>
<style>
body{font-family:Arial;background:#111;color:#fff;margin:0;padding:10px}
#chatBox{height:60vh;overflow-y:auto;border:1px solid #333;padding:10px;border-radius:10px;background:#1a1a1a}
.msg{margin:10px 0;padding:10px;border-radius:8px;word-break:break-word}
.user{background:#2a5bd7;text-align:right}
.bot{background:#222}
.controls{display:flex;gap:5px;margin-top:10px;flex-wrap:wrap}
input,select{padding:10px;border-radius:8px;border:none;flex:1;min-width:120px}
button{padding:10px 12px;border-radius:8px;border:none;background:#2a5bd7;color:#fff;font-weight:bold;cursor:pointer}
img,video{max-width:100%;margin-top:10px;border-radius:10px}
a{color:#5af}
</style>
</head>
<body>
<h2>🤖 FRIDAY AI PRO MAX</h2>
<div id="chatBox"><div class="msg bot">Hi boss! Bolo kya banana hai? Image, Video, PDF, Voice sab banega.</div></div>
<div class="controls">
<input id="userInput" placeholder="Kuch bhi likho... e.g. A logo for Gupta Classes">
</div>
<div class="controls">
<select id="style">
<option value="realistic">Realistic</option>
<option value="anime">Anime</option>
<option value="3d render">3D</option>
<option value="logo design">Logo</option>
<option value="poster art">Poster</option>
<option value="cinematic">Cinematic</option>
<option value="cartoon">Cartoon</option>
</select>
<button onclick="sendMessage()">💬 Chat</button>
<button onclick="startListening()">🎤 Mic</button>
</div>
<div class="controls">
<button onclick="generateImage()">🖼️ Image</button>
<button onclick="generateVideo()">🎬 Video</button>
<button onclick="speakLast()">🔊 Voice</button>
<button onclick="generateDoc()">📄 PDF</button>
</div>
<script>
const chatBox = document.getElementById('chatBox');
let lastBotReply = "Hi boss! Bolo kya banana hai?";
function addMsg(text, type){
    chatBox.innerHTML += `<div class="msg ${type}">${text}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
}
async function sendMessage(){
    let input = document.getElementById('userInput');
    let msg = input.value; if(!msg) return;
    addMsg(msg, 'user'); input.value = "";
    let res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    let data = await res.json(); lastBotReply = data.reply;
    addMsg(data.reply, 'bot');
}
async function generateImage(){
    let prompt = document.getElementById('userInput').value;
    let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle kuch likho!");
    addMsg(`🖼️ Image: ${prompt} (${style})`, 'user');
    let res = await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json();
    addMsg(`<b>${d.prompt}</b><br><img src="${d.image_url}"><br><a href="${d.image_url}" target="_blank">⬇️ Download</a>`, 'bot');
}
async function generateVideo(){
    let prompt = document.getElementById('userInput').value;
    let style = document.getElementById('style').value;
    if(!prompt) return alert("Pehle kuch likho!");
    addMsg(`🎬 Video: ${prompt}... (30-50 sec lagega)`, 'user');
    let res = await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json();
    addMsg(`<b>${d.prompt}</b><br><video src="${d.video_url}" controls autoplay loop></video>`, 'bot');
}
async function speakLast(){
    let res = await fetch('/speak',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:lastBotReply})});
    let d = await res.json(); new Audio(d.audio_url).play();
}
function startListening(){
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang = 'en-IN'; rec.start();
    rec.onresult = e => { document.getElementById('userInput').value = e.results[0][0].transcript; sendMessage(); }
}
async function generateDoc(){
    let content = document.getElementById('userInput').value;
    if(!content) return alert("PDF me kya likhna hai wo likho");
    let res = await fetch('/generate-doc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'pdf', content})});
    let d = await res.json();
    addMsg(`<a href="${d.file_url}" download>📄 Download PDF</a>`, 'bot');
}
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
    return jsonify({"reply": f"Samajh gaya boss: {msg}. Ab Image ya Video button dabao."})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt','')
    style = request.json.get('style','realistic')
    full_prompt = f"{prompt}, {style} style, highly detailed, 8k"
    safe_prompt = requests.utils.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&model=flux&enhance=true&nologo=true&seed={uuid.uuid4().hex[:4]}"
    return jsonify({"image_url": image_url, "prompt": full_prompt})

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
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(path)
    return jsonify({"file_url": f"/static/{filename}"})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
