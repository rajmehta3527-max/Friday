from flask import Flask, request, jsonify
import requests, re, os
from urllib.parse import quote

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FRIDAY - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;background:#F6F3EE;color:#1A1A1A;font-family:'Inter',sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden}
.header{padding:16px 22px;background:#fff;border-bottom:1px solid #E8E2D9;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:18px;letter-spacing:1px}
.header span{font-size:10px;border:1px solid #E8E2D9;padding:5px 12px;border-radius:100px;color:#8C857B;font-weight:600}
#chat{flex:1;overflow-y:auto;padding:22px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:85%;padding:14px 18px;border-radius:18px;line-height:1.7;font-size:14.5px;white-space:pre-wrap;word-wrap:break-word;animation:pop.2s ease}
@keyframes pop{from{transform:translateY(5px);opacity:0}to{transform:translateY(0);opacity:1}}
.user{align-self:flex-end;background:#1A1A1A;color:#fff;border-bottom-right-radius:6px}
.bot{align-self:flex-start;background:#fff;border:1px solid #E8E2D9;font-family:'Libre Baskerville',serif;border-bottom-left-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,.03)}
.footer{padding:14px 18px;background:#fff;border-top:1px solid #E8E2D9;display:flex;gap:10px;align-items:center}
input{flex:1;background:#F6F3EE;border:1px solid #E8E2D9;padding:14px 18px;border-radius:100px;outline:none;font-family:'Inter';font-size:15px}
button{border:none;background:#1A1A1A;color:#fff;padding:14px 22px;border-radius:100px;font-weight:600;cursor:pointer;font-size:14px}
button:hover{background:#333}
.credit{text-align:center;font-size:11px;color:#8C857B;padding:8px;background:#fff;border-top:1px solid #f0ebe3}
.typing{font-size:12px;color:#8C857B;padding:0 22px 8px;display:none}
</style>
</head>
<body>
<div class="header"><h2>FRIDAY</h2><span>BY RAJ MEHTA • GROQ POWERED</span></div>
<div id="chat"><div class="msg bot">Hey! I'm FRIDAY by Raj Mehta (18, @rajmehta_087). Built with Groq Llama 3.3 - I'm super fast now! Ask me anything 🚀</div></div>
<div class="typing" id="typing">Friday is thinking...</div>
<div class="footer"><input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button></div>
<div class="credit">Made with ❤️ by <b>Raj Mehta</b> | @rajmehta_087 | Groq AI</div>
<script>
const chat=document.getElementById('chat'); const typing=document.getElementById('typing');
function add(t,c){ const d=document.createElement('div'); d.className='msg '+c; d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return; add(m,'user'); i.value=''; typing.style.display='block';
 let l=add('...','bot');
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  let j=await r.json(); l.innerText=j.reply;
 }catch{ l.innerText='Error, try again'; }
 typing.style.display='none';
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body>
</html>
"""

DEV_INFO = """I am FRIDAY, created by Raj Mehta.

👨‍💻 Developer: Raj Mehta
🎂 Age: 18 years old
📸 Instagram: @rajmehta_087
🚀 Engine: Groq Llama 3.3 70B (Super Fast)
📍 From: India

Raj built me as his personal AI assistant. I am now powered by Groq for ultra-fast responses!"""

def is_about_dev(q):
    q=q.lower()
    return any(k in q for k in ["who made you","who created you","your developer","your dev","about dev","who is raj","kisne banaya","who are you","tell about yourself"])

def get_groq_answer(prompt):
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY is not set in Render. Please add it in Environment."
    if not GROQ_API_KEY.startswith("gsk_"):
        return f"ERROR: Invalid Groq key format. Your key is {len(GROQ_API_KEY)} chars and should start with gsk_. Get correct key from console.groq.com/keys"
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are FRIDAY, a helpful AI assistant created by Raj Mehta, 18 years old, Instagram @rajmehta_087. You are friendly, concise, knowledgeable. If asked about US dollar or any topic, give accurate, helpful answer. You are powered by Groq."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        else:
            return f"Groq API Error {r.status_code}: {r.text[:500]}. Check if your key is valid at console.groq.com/keys"
    except Exception as e:
        return f"Connection Error: {str(e)}"

@app.route('/')
def home():
    return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m = request.json.get('message','').strip()
    if not m:
        return jsonify({"reply": "Ask something..."})

    if is_about_dev(m):
        return jsonify({"reply": DEV_INFO})

    ans = get_groq_answer(m)
    ans = re.sub(r'\*\*', '', ans)
    return jsonify({"reply": ans[:5000]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
