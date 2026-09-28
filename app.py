from flask import Flask, request, jsonify, send_from_directory
from fpdf import FPDF
import os, uuid, requests

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Friday AI - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;background:#F6F3EE;color:#1A1A1A;font-family:'Inter',sans-serif}
.header{padding:16px 20px;background:#FFFFFF;border-bottom:1px solid #E8E2D9;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:20}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:18px}
.header span{font-size:11px;border:1px solid #E8E2D9;padding:4px 10px;border-radius:100px;color:#8C857B}
#chatBox{height:calc(100vh - 155px);overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:82%;padding:14px 16px;border-radius:14px;line-height:1.65;font-size:14.5px;white-space:pre-wrap}
.user{align-self:flex-end;background:#1A1A1A;color:#F6F3EE;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#FFFFFF;border:1px solid #E8E2D9;border-bottom-left-radius:4px;font-family:'Libre Baskerville',serif;color:#2B2B2B;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.bot img{max-width:300px;max-height:42vh;object-fit:contain;border-radius:10px;margin-top:10px;cursor:zoom-in;display:block;border:1px solid #E8E2D9}
.bot video{max-width:300px;border-radius:10px;margin-top:10px}
.footer{padding:12px 16px;background:#FFFFFF;border-top:1px solid #E8E2D9;position:fixed;bottom:0;width:100%;z-index:20}
.input-row{display:flex;gap:8px}
#userInput{flex:1;background:#F6F3EE;border:1px solid #E8E2D9;padding:12px 16px;border-radius:100px;outline:none;font-family:'Inter',sans-serif}
.btn{border:1px solid #E8E2D9;background:#FFF;color:#1A1A1A;padding:9px 14px;border-radius:100px;font-weight:500;cursor:pointer;font-size:13px}
.btn-primary{background:#1A1A1A;color:#FFF;border-color:#1A1A1A}
.actions{display:flex;gap:6px;margin-top:10px}
a.dl{display:inline-block;margin-top:10px;background:#1A1A1A;color:#fff;padding:7px 14px;border-radius:100px;text-decoration:none;font-size:12px}
.credit{text-align:center;font-size:11px;color:#8C857B;margin-top:10px}
.credit b{color:#1A1A1A} .credit a{color:#1A1A1A;text-decoration:underline;font-weight:600}
#imgModal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(246,243,238,0.95);z-index:999;justify-content:center;align-items:center;padding:20px}
#imgModal img{max-width:95%;max-height:90%;border-radius:12px}
#imgModal span{position:absolute;top:18px;right:22px;font-size:28px;cursor:pointer}
</style>
</head>
<body>
<div class="header"><h2>FRIDAY — AI STUDIO</h2><span>MADE BY RAJ MEHTA</span></div>
<div id="chatBox"><div class="msg bot">Hello, I am Friday — Your personal AI assistant.\n\nI can do everything:\n• Answer any question\n• Write essays, code, captions\n• Generate Images\n• Generate Videos\n• Make PDFs\n\nJust type and press Send. For image, type prompt and press Image button.</div></div>
<div id="imgModal" onclick="this.style.display='none'"><span>×</span><img id="modalImg"></div>
<div class="footer">
<div class="input-row"><input id="userInput" placeholder="Ask anything or write image prompt..."><button class="btn btn-primary" onclick="sendMessage()">Send</button></div>
<div class="actions">
<select id="style" class="btn"><option value="realistic photorealistic">📸 Realistic</option><option value="cinematic">🎬 Cinematic</option><option value="anime">🎨 Anime</option><option value="minimal logo vector">💎 Logo</option></select>
<button class="btn btn-primary" onclick="generateImage()">🖼️ Image</button>
<button class="btn" onclick="generateVideo()">🎬 Video</button>
<button class="btn" onclick="generateDoc()">📄 PDF</button>
</div>
<div class="credit">Made with ❤️ by <b>Raj Mehta</b> (Age 18) | Instagram: <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>
</div>
<script>
const chatBox = document.getElementById('chatBox');
function addMsg(text, type){
  const div = document.createElement('div'); div.className='msg '+type; div.innerHTML=text;
  const imgs = div.querySelectorAll('img'); imgs.forEach(img=>{ img.onclick=()=>{ document.getElementById('modalImg').src=img.src; document.getElementById('imgModal').style.display='flex'; } });
  chatBox.appendChild(div); chatBox.scrollTop = chatBox.scrollHeight; return div;
}
async function sendMessage(){
    let input = document.getElementById('userInput'); let msg = input.value.trim(); if(!msg) return;
    addMsg(msg, 'user'); input.value = "";
    const typing = addMsg('Thinking...', 'bot');
    try{
        let res = await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
        let data = await res.json(); typing.remove();
        addMsg(data.reply, 'bot');
    }catch(e){ typing.innerHTML='Error, try again'; }
}
async function generateImage(){
    let prompt = document.getElementById('userInput').value; let style = document.getElementById('style').value;
    if(!prompt) return alert("Prompt likho!"); addMsg(prompt, 'user');
    const load = addMsg('Generating image (no watermark)...', 'bot');
    let res = await fetch('/generate-image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt, style})});
    let d = await res.json(); load.remove();
    addMsg(`${d.final_prompt}<br><img src="${d.image_url}"><br><a class="dl" href="${d.image_url}" target="_blank">Download HD</a>`, 'bot');
}
async function generateVideo(){
    let prompt = document.getElementById('userInput').value;
    if(!prompt) return alert("Video prompt likho!");
    addMsg(prompt, 'user');
    const load = addMsg('Generating video... 30 sec wait', 'bot');
    let res = await fetch('/generate-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});
    let d = await res.json(); load.remove();
    addMsg(`<video src="${d.video_url}" controls autoplay loop muted playsinline></video><br><a class="dl" href="${d.video_url}" target="_blank">Download Video</a>`, 'bot');
}
async function generateDoc(){
    let content = document.getElementById('userInput').value; if(!content) return alert("PDF text likho");
    let res = await fetch('/generate-doc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content})});
    let d = await res.json(); addMsg(`<a class="dl" href="${d.file_url}" download>Download PDF</a>`, 'bot');
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
    user_msg = request.json.get('message','')
    try:
        # AI API - answers everything
        url = f"https://text.pollinations.ai/{requests.utils.quote(user_msg)}"
        r = requests.get(url, params={"model":"openai", "system":"You are Friday AI, made by Raj Mehta (18, insta @rajmehta_087). Answer helpfully in simple language. Keep answers concise."}, timeout=25)
        reply = r.text.strip() if r.status_code==200 else "I'm Friday by Raj Mehta. I can help!"
    except:
        reply = f"Hello! I'm Friday made by Raj Mehta. You asked: {user_msg}. I can answer any question, write code, essays, and generate images/videos."
    return jsonify({"reply": reply[:3000]})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    prompt = request.json.get('prompt','')
    style = request.json.get('style','realistic')
    full = f"{prompt}, {style}, ultra detailed, sharp, no watermark, no logo, no text, clean"
    safe = requests.utils.quote(full)
    img_url = f"https://image.pollinations.ai/prompt/{safe}?width=768&height=1024&model=flux&enhance=true&nologo=true&nofeed=true&private=true&seed={uuid.uuid4().hex[:5]}"
    return jsonify({"image_url": img_url, "final_prompt": full})

@app.route('/generate-video', methods=['POST'])
def generate_video():
    prompt = request.json.get('prompt','')
    safe = requests.utils.quote(f"{prompt}, cinematic video, smooth motion, 4k")
    vid_url = f"https://image.pollinations.ai/prompt/{safe}?model=turbo&video=true&nologo=true&enhance=true"
    return jsonify({"video_url": vid_url})

@app.route('/generate-doc', methods=['POST'])
def generate_doc():
    content = request.json.get('content','')
    fname = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join("static", fname)
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Times", size=12); pdf.multi_cell(0, 8, content); pdf.output(path)
    return jsonify({"file_url": f"/static/{fname}"})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
