from flask import Flask, request, jsonify, render_template
from gtts import gTTS
from fpdf import FPDF
from docx import Document
import openpyxl, os, uuid, requests

app = Flask(__name__)
os.makedirs("static", exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message')
    return jsonify({"reply": f"Friday: {msg} samajh gaya boss."})

# --- IMAGE GENERATOR - KISI BHI TARAH KI ---
@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    style = data.get('style', 'realistic') # realistic, anime, 3d, logo, poster, cinematic
    
    # Style ko prompt me add kar rahe hain taaki kisi bhi tarah ki ban jaye
    full_prompt = f"{prompt}, {style} style, highly detailed, 8k, ultra realistic"
    safe_prompt = requests.utils.quote(full_prompt)
    
    # Flux PRO - sabse powerful free model, kisi bhi style ki image
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1280&height=720&model=flux&enhance=true&nologo=true&seed={uuid.uuid4().hex[:4]}"
    
    return jsonify({
        "image_url": image_url,
        "prompt": full_prompt,
        "download_url": image_url
    })

# --- VIDEO GENERATOR - KISI BHI TARAH KA ---
@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.json
    prompt = data.get('prompt', '')
    style = data.get('style', 'cinematic') # cinematic, anime, 3d, realistic, cartoon
    
    full_prompt = f"{prompt}, {style} video, smooth motion, 4k, highly detailed"
    safe_prompt = requests.utils.quote(full_prompt)
    
    # Video model - kisi bhi tarah ka video
    video_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=video&nologo=true&enhance=true"
    
    return jsonify({
        "video_url": video_url,
        "prompt": full_prompt
    })

# --- VOICE ---
@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text','')[:600]
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    path = os.path.join("static", filename)
    tts = gTTS(text=text, lang='en', tld='co.in')
    tts.save(path)
    return jsonify({"audio_url": f"/static/{filename}"})

# --- DOCS ---
@app.route('/generate-doc', methods=['POST'])
def generate_doc():
    doc_type = request.json.get('type')
    content = request.json.get('content','')
    filename = uuid.uuid4().hex
    if doc_type == 'pdf':
        p = f"static/{filename}.pdf"
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial",12); pdf.multi_cell(0,10,content); pdf.output(p)
        return jsonify({"file_url": f"/{p}"})
    return jsonify({"error":"invalid"}),400

if __name__ == '__main__':
    app.run(debug=True)
