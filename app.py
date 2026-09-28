from flask import Flask, request, jsonify
import requests, re, os

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LIA - by Raj Mehta</title>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}body{margin:0;background:#FDF8F6;color:#1A1A1A;font-family:'Inter',sans-serif;display:flex;flex-direction:column;height:100vh;overflow:hidden}
.header{padding:16px 22px;background:#fff;border-bottom:1px solid #F0E6E0;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:18px}.header span{font-size:10px;border:1px solid #F0E6E0;padding:5px 12px;border-radius:100px;color:#A89A90}
#chat{flex:1;overflow-y:auto;padding:22px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:85%;padding:14px 18px;border-radius:18px;line-height:1.7;font-size:14.5px;white-space:pre-wrap}
.user{align-self:flex-end;background:#1A1A1A;color:#fff;border-bottom-right-radius:6px}
.bot{align-self:flex-start;background:#fff;border:1px solid #F0E6E0;font-family:'Libre Baskerville',serif;border-bottom-left-radius:6px}
.footer{padding:14px 18px;background:#fff;border-top:1px solid #F0E6E0;display:flex;gap:10px}
input{flex:1;background:#FDF8F6;border:1px solid #F0E6E0;padding:14px 18px;border-radius:100px;outline:none}
button{border:none;background:#1A1A1A;color:#fff;padding:14px 22px;border-radius:100px;font-weight:600;cursor:pointer}
</style>
</head>
<body>
<div class="header"><h2>LIA</h2><span>BY RAJ MEHTA</span></div>
<div id="chat"><div class="msg bot">Hey! I'm LIA by Raj Mehta (18, @rajmehta_087). Ask me anything ✨</div></div>
<div class="footer"><input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button></div>
<script>
const chat=document.getElementById('chat');
function add(t,c){ const d=document.createElement('div'); d.className='msg '+c; d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return; add(m,'user'); i.value='';
 let l=add('...','bot');
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  let j=await r.json(); l.innerText=j.reply;
 }catch{ l.innerText='Error'; }
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body>
</html>
"""

DEV_INFO = "I am LIA, created by Raj Mehta.\n\n👨‍💻 Developer: Raj Mehta\n🎂 Age: 18\n📸 Instagram: @rajmehta_087\n🤖 Name: LIA"

def is_about_dev(q):
    q=q.lower()
    return any(k in q for k in ["who made you","your developer","who is raj","kisne banaya","your name","who are you"])

def get_lia_answer(prompt):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not set in Render. Add it from console.groq.com/keys"

    # Ye 5 models Groq pe abhi active hai - ek fail hoga to dusra try hoga
    MODELS_TO_TRY = [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "gemma2-9b-it"
    ]

    for model in MODELS_TO_TRY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are LIA, created by Raj Mehta (18, @rajmehta_087). Your name is LIA only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            r = requests.post(url, json=payload, headers=headers, timeout=25)
            if r.status_code == 200:
                print(f"Working model: {model}")
                return r.json()['choices'][0]['message']['content']
            else:
                print(f"Model {model} failed: {r.text[:200]}")
                continue
        except Exception as e:
            print(f"Model {model} exception: {e}")
            continue

    return "All Groq models failed. Go to console.groq.com -> check if your API key is valid and you have credits. Your key should start with gsk_"

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m = request.json.get('message','').strip()
    if is_about_dev(m): return jsonify({"reply": DEV_INFO})
    ans = get_lia_answer(m)
    return jsonify({"reply": re.sub(r'\*\*','',ans)[:5000]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
