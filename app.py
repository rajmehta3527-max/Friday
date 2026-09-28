from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head><title>Friday AI</title></head>
    <body style="font-family:sans-serif; text-align:center; margin-top:100px;">
        <h1>Friday AI is Live! ✅</h1>
        <p>Ab Gradio ka error khatam. Ye Flask pe chal raha hai.</p>
        <input type="text" id="msg" placeholder="Kuch likh..." style="padding:10px; width:300px;">
        <button onclick="send()" style="padding:10px;">Send</button>
        <p id="reply"></p>
        <script>
        function send(){
            let m = document.getElementById('msg').value;
            document.getElementById('reply').innerText = "Friday: You said - " + m;
        }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
