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
#chat{flex:1;overflow-y:auto;padding:16px;padding-bottom:100px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:85%;padding:12px 16px;border-radius:18px;font-size:15px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.user{align-self:flex-end;background:#111;color:#fff;border-bottom-right-radius:4px}
.bot{align-self:flex-start;background:#fff;border:1px solid #eee;border-bottom-left-radius:4px;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.footer{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;z-index:9999}
.input-row{height:60px;display:flex;align-items:center;gap:8px;padding:8px 12px;}
.input-row input{flex:1;height:44px;background:#f5f3f0;border:1.5px solid #e5ddd5;border-radius:24px;padding:0 18px;font-size:16px;outline:none}
.input-row button{height:44px;min-width:70px;background:#111;color:#fff;border:none;border-radius:24px;font-weight:600}
.credit{height:28px;display:flex;align-items:center;justify-content:center;gap:6px;font-size:11px;color:#888;background:#fff;padding-bottom:env(safe-area-inset-bottom)}
.credit a{color:#111;font-weight:600;text-decoration:none;border-bottom:1px dashed #111}
.badge{font-size:10px;padding:3px 8px;border-radius:10px;margin-bottom:4px;display:inline-block;font-weight:600}
.live{background:#E8F5E9;color:#2E7D32}.weather{background:#E3F2FD;color:#1565C0}
</style>
</head>
<body>
<div class="header"><h2>LIA</h2><span>BY RAJ MEHTA</span></div>
<div id="chat"><div class="msg bot">Hey! I'm LIA made by Raj Mehta 🌐✨\n\nAsk me anything - weather, news, president, studies - sab live bataungi!</div></div>
<div class="footer">
  <div class="input-row"><input id="inp" type="text" placeholder="Ask anything..." autocomplete="off"/><button onclick="send()">Send</button></div>
  <div class="credit">Made by Raj Mehta • <a href="https://instagram.com/rajmehta_087" target="_blank">@rajmehta_087</a></div>
</div>
<script>
const chat=document.getElementById('chat');
function add(t,c,isHtml=false){ const d=document.createElement('div'); d.className='msg '+c; if(isHtml) d.innerHTML=t; else d.innerText=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; return d; }
async function send(){
 let i=document.getElementById('inp'); let m=i.value.trim(); if(!m) return; add(m,'user'); i.value='';
 let l=add('Thinking...','bot');
 try{
  let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
  let j=await r.json(); l.innerHTML=j.reply;
 }catch{ l.innerText='Server Error'; }
}
document.getElementById('inp').addEventListener('keypress',e=>{ if(e.key==='Enter') send(); });
</script>
</body></html>
"""

DEV_INFO = "I'm LIA made by Raj Mehta"

def is_about_dev(q): return any(k in q.lower() for k in ["who made you","who are you","your name","who created you"])

def needs_internet(q):
    q=q.lower()
    return any(k in q for k in ["president","weather","mausam","news","today","price","score","who is","what is","2025","2026","trump"])

def get_weather(city=""):
    try:
        city_clean = city.replace("weather","").replace("mausam","").strip()
        if city_clean.lower() in ["weather","mausam",""]: city_clean=""
        j = requests.get(f"https://wttr.in/{quote(city_clean)}?format=j1", timeout=7).json()
        curr=j['current_condition'][0]; area=j['nearest_area'][0]['areaName'][0]['value']
        return f"Live Weather for {area}: {curr['weatherDesc'][0]['value']}, {curr['temp_C']}°C, Humidity {curr['humidity']}%"
    except: return None

def search_web(query):
    try:
        r=requests.get(f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1", timeout=7).json()
        txt=r.get("AbstractText","")
        if not txt and r.get("RelatedTopics"):
            for t in r["RelatedTopics"][:2]:
                if isinstance(t,dict) and t.get("Text"): txt+=t["Text"]+" "
        if not txt:
            w=requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query)}", timeout=5)
            if w.status_code==200: txt=w.json().get("extract","")
        return txt[:2000] if txt else None
    except: return None

def get_lia_answer(prompt, web_context=None, is_weather=False):
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY not set in Render. Go to Render > Environment > Add GROQ_API_KEY"

    system = "You are LIA. Identity: I'm LIA made by Raj Mehta. Never say Meta AI or Llama. If asked who made you, say I'm LIA made by Raj Mehta. Friendly, concise."
    if is_weather: system+=f" LIVE weather: {web_context}"
    elif web_context: system+=f" LIVE data: {web_context}. Current US President is Donald Trump (47th)."

    # FIXED - Latest working Groq models 2026
    MODELS = ["llama-3.1-8b-instant","llama-3.3-70b-versatile","gemma2-9b-it","openai/gpt-oss-20b","openai/gpt-oss-120b"]

    last_error="Unknown"
    for model in MODELS:
        try:
            resp=requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":prompt}],"temperature":0.6},
                timeout=20)
            if resp.status_code==200:
                return resp.json()['choices'][0]['message']['content']
            else:
                last_error=f"{model} -> {resp.status_code}: {resp.text[:200]}"
                print(last_error)
                if resp.status_code==401: return "ERROR: API Key galat hai. Groq me new key banao aur Render pe update karo."
                if resp.status_code==429: continue # rate limit, try next model
        except Exception as e:
            last_error=str(e)
            continue

    return f"Groq Error: {last_error}. Check API key in Render."

@app.route('/')
def home(): return HTML

@app.route('/chat', methods=['POST'])
def chat_api():
    m=request.json.get('message','').strip()
    if not m: return jsonify({"reply":"Ask something"})
    if is_about_dev(m): return jsonify({"reply":DEV_INFO})

    if "weather" in m.lower() or "mausam" in m.lower():
        wd=get_weather(m)
        if wd:
            ans=get_lia_answer(m,wd,True)
            return jsonify({"reply": f"<span class='badge weather'>🌦️ LIVE WEATHER</span><br>{ans}"})

    web_data=search_web(m) if needs_internet(m) else None
    badge="<span class='badge live'>🌐 LIVE</span><br>" if web_data else ""
    ans=get_lia_answer(m,web_data)
    return jsonify({"reply": badge + re.sub(r'\*\*','',ans).replace("\n","<br>")})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
