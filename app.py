from flask import Flask, request, jsonify
import requests, re, os
from urllib.parse import quote

app = Flask(__name__)

# Gemini key Render ke Environment se aayega
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

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
.header{padding:14px 20px;background:#fff;border-bottom:1px solid #E8E2D9;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-family:'Libre Baskerville',serif;font-size:16px}
.header span{font-size:10px;border:1px solid #E8E2D9;padding:4px 10px;border-radius:100px;color:#8C857B}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:14px;line-height:1.7;font-size:14px;white-space:pre-wrap;word-wrap:break-word}
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
  let j=await r.json(); l.innerText=j.reply;
 }catch{ l.innerText='Error, try again'; }
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

Raj is a young developer from India who built me as his personal AI assistant. He loves coding, AI, and building cool projects."""

def is_about_dev(q):
    q = q.lower()
    keys = ["who made you", "who created you", "your developer", "your dev", "about dev", "about developer", "who is raj", "who is raj mehta", "your name", "your owner", "kisne banaya", "tumhe kisne banaya", "your creator", "who are you"]
    return any(k in q for k in keys)

def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{quote(city)}?format=j1", timeout=7)
        if r.status_code == 200:
            curr = r.json()['current_condition'][0]
            temp = curr['temp_C']
            desc = curr['weatherDesc'][0]['value']
            humidity = curr['humidity']
            wind = curr['windspeedKmph']
            return f"Weather in {city.title()} right now:\n🌡️ Temp: {temp}°C\n☁️ Condition: {desc}\n💧 Humidity: {humidity}%\n💨 Wind: {wind} km/h\n\nLive data"
    except:
        pass
    return None

def get_gemini_answer(prompt):
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        data = {
            "contents": [{
                "parts": [{"text": f"You are FRIDAY, created by Raj Mehta (18, Instagram @rajmehta_087). Be helpful, short, friendly. Answer this: {prompt}"}]
            }]
        }
        r = requests.post(url, json=data, timeout=25)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print("Gemini Error:", r.text)
            return None
    except Exception as e:
        print("Exception:", e)
        return None

def get_pollinations_fallback(msg):
    try:
        r = requests.get(f"https://text.pollinations.ai/{quote(msg)}?model=openai", timeout=10)
        if r.status_code == 200 and len(r.text) > 20:
            return r.text
    except:
        pass
    return None

@app.route('/')
def home():
    return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m = request.json.get('message', '').strip()
    if not m:
        return jsonify({"reply": "Ask something..."})

    # 1. Dev info - instant
    if is_about_dev(m):
        return jsonify({"reply": DEV_INFO})

    # 2. Weather - real data
    if "weather" in m.lower():
        city = m.lower().replace("weather of","").replace("weather in","").replace("weather","").strip()
        if not city:
            city = "rishikesh"
        w = get_weather(city)
        if w:
            return jsonify({"reply": w})

    # 3. Real AI - Gemini
    ans = get_gemini_answer(m)

    # 4. Fallback if Gemini fails
    if not ans:
        ans = get_pollinations_fallback(m)

    # 5. Final fallback
    if not ans:
        ans = "I'm FRIDAY by Raj Mehta. Gemini key is not working. Please check in Render Environment that GEMINI_API_KEY is set correctly and redeploy with Clear Cache."

    ans = re.sub(r'\*\*', '', ans)
    return jsonify({"reply": ans[:4000]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
