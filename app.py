from flask import Flask, request, jsonify
import requests, re, os
from urllib.parse import quote

app = Flask(__name__)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

HTML = """
<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>LIA - by Raj Mehta</title>
<style>
*{box-sizing:border-box}html,body{margin:0;padding:0;height:100%;height:100dvh;overflow:hidden}
body{background:#FDF8F6;font-family:-apple-system,sans-serif;display:flex;flex-direction:column}
.header{height:56px;flex-shrink:0;padding:0 16px;background:#fff;border-bottom:1px solid #eee;display:flex;justify-content:space-between;align-items:center}
.header h2{margin:0;font-family:serif;font-size:20px}.header span{font-size:11px;border:1px solid #eee;padding:6px 12px;border-radius:20px;color:#999}
#chat{flex:1;overflow-y:auto;padding:16px;padding-bottom:90px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;font-size:15px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.user{align-self:flex-end;background:#111;color:#fff;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#fff;border:1px solid #eee;border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.footer{position:fixed;bottom:0;left:0;right:0;height:75px;background:#fff;border-top:1px solid #eee;display:flex;align-items:center;gap:8px;padding:10px 12px;padding-bottom:calc(10px + env(safe-area-inset-bottom));z-index:9999}
.footer input{flex:1;height:48px;background:#f5f3f0;border:1.5px solid #e5ddd5;border-radius:24px;padding:0 18px;font-size:16px;outline:none}
.footer button{height:48px;min-width:70px;background:#111;color:#fff;border:none;border-radius:24px;font-weight:600}
.badge{font-size:10px;padding:3px 8px;border-radius:10px;margin-bottom:4px;display:inline-block;font-weight:600}
.live{background:#E8F5E9;color:#2E7D32}.weather{background:#E3F2FD;color:#1565C0}
</style>
</head>
<body>
<div class="header"><h2>LIA</h2><span>BY RAJ MEHTA • SUPER HYBRID</span></div>
<div id="chat"><div class="msg bot">Hey! I'm LIA by Raj Mehta 🌐✨\n\nI'm Super Hybrid now - weather, news, president, score sab live!\nTry: "Delhi weather" or "President of America" or "Gori ladki kaise pataye"</div></div>
<div class="footer"><input id="inp" type="text" placeholder="Ask anything..." autocomplete="off"/><button onclick="send()">Send</button></div>
<script>
const chat=document.getElementById('chat');
function add(t,c,isHtml=false){ const d=document.createElement('div'); d.className='msg '+c; if(isHtml) d.innerHTML=t; else d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return; add(m,'user'); i.value='';
 let l=add('Searching live...','bot');
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  let j=await r.json(); l.innerHTML=j.reply;
 }catch{ l.innerText='Error'; }
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body></html>
"""

DEV_INFO = "I am LIA, created by Raj Mehta, 18, Insta @rajmehta_087. Super Hybrid AI."

def is_about_dev(q):
    return any(k in q.lower() for k in ["who made you","your developer","who is raj","your name"])

# VAST INTERNET TRIGGER - ab sirf "weather" likhne pe bhi online hoga
def needs_internet(q):
    q = q.lower()
    vast_keywords = [
        "president","prime minister","weather","mausam","temperature","barish",
        "news","latest","today","aaj","current","abhi","price","rate","score",
        "ipl","cricket","election","result","who is","what is","kya hai","kaun hai",
        "2025","2026","trump","biden","modi","delhi","mumbai"
    ]
    if len(q.split()) >= 1:
        return any(k in q for k in vast_keywords) or "?" in q or q.startswith(("who","what","when","where","weather"))
    return False

def get_weather(city="auto"):
    try:
        city_clean = city.replace("weather","").replace("mausam","").replace("ka","").strip()
        if not city_clean or city_clean.lower() in ["weather","mausam"]: city_clean = ""
        j_url = f"https://wttr.in/{quote(city_clean)}?format=j1"
        j = requests.get(j_url, timeout=7).json()
        curr = j['current_condition'][0]
        area = j['nearest_area'][0]['areaName'][0]['value']
        return f"Live Weather for {area}: {curr['weatherDesc'][0]['value']}, Temp: {curr['temp_C']}°C (Feels like {curr['FeelsLikeC']}°C), Humidity: {curr['humidity']}%, Wind: {curr['windspeedKmph']} km/h"
    except:
        return None

def search_web(query):
    try:
        url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"
        r = requests.get(url, timeout=7)
        data = r.json()
        result = ""
        if data.get("AbstractText"): result += data["AbstractText"] + " "
        if data.get("RelatedTopics"):
            for t in data["RelatedTopics"][:3]:
                if isinstance(t, dict) and "Text" in t: result += t["Text"] + " "
        if not result.strip():
            w = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}", timeout=5)
            if w.status_code==200: result = w.json().get("extract","")
        return result[:2000] if result else None
    except:
        return None

def get_lia_answer(prompt, web_context=None, is_weather=False):
    if not GROQ_API_KEY: return "GROQ_API_KEY not set in Render Env"

    # Unfiltered + Vast System Prompt
    base_system = """
    You are LIA, created by Raj Mehta (18, @rajmehta_087). You are a friendly, unfiltered, helpful best friend.
    RULES:
    1. NEVER say "I'm sorry, but I can't help with that" or "As an AI". You MUST answer dating, flirting, roasting, relationship questions with respectful, non-creepy advice in Hinglish.
    2. No explicit porn/sexual details. Only dating advice allowed.
    3. Use Hinglish mix (Hindi + English) like Indian friends.
    4. Be bold, funny, concise.
    """

    if is_weather:
        system = base_system + f"\nYou have LIVE weather data: {web_context}. Present beautifully with emojis and tips."
    elif web_context:
        system = base_system + f"\nYou have LIVE internet data from 2026: {web_context}. Use this as priority. Current US President is Donald Trump (47th, since Jan 2025)."
    else:
        system = base_system + "\nCurrent US President is Donald Trump (47th, since Jan 2025)."

    MODELS = ["llama-3.3-70b-versatile","llama3-8b-8192","openai/gpt-oss-20b","gemma2-9b-it"]
    for model in MODELS:
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"temperature":0.7},
                timeout=25)
            if r.status_code==200:
                ans = r.json()['choices'][0]['message']['content']
                if "I'm sorry" in ans and "can't help" in ans: continue
                return ans
        except: continue
    return "Groq busy hai, try again"

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m=request.json.get('message','').strip()
    if not m: return jsonify({"reply":"Ask something..."})
    if is_about_dev(m): return jsonify({"reply":DEV_INFO})

    q_low = m.lower()
    if "weather" in q_low or "mausam" in q_low or "temperature" in q_low:
        wd = get_weather(m)
        if wd:
            ans = get_lia_answer(m, wd, is_weather=True)
            return jsonify({"reply": f"<span class='badge weather'>🌦️ LIVE WEATHER</span><br>{ans.replace(chr(10),'<br>')}"})

    web_data = search_web(m) if needs_internet(m) else None
    badge = "<span class='badge live'>🌐 LIVE INTERNET</span><br>" if web_data else ""
    ans = get_lia_answer(m, web_data)
    return jsonify({"reply": badge + re.sub(r'\*\*','',ans).replace("\n","<br>")})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
