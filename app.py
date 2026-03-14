from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
import os
from translator import translate_text
from file_handler import read_txt, read_pdf, read_docx, write_txt
from googletrans import Translator

translator = Translator()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
# Add logger=True so you can see connection errors in Render logs
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode='eventlet', 
                    engineio_logger=True, 
                    logger=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Languages configuration (same as in ui.py)
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Marathi": "mr",
    "Urdu": "ur",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml"
}

socketio = SocketIO(app, 
                    async_mode='eventlet', 
                    cors_allowed_origins="*")

@socketio.on('realtime_translation')
def handle_realtime(data):
    # 1. Get data safely
    text = data.get('text')
    src_lang = data.get('src_lang', 'en')  # Default to 'en'
    dest_lang = data.get('dest_lang', 'hi') # Default to 'hi'

    print(f"Received for translation: {text} from {src_lang} to {dest_lang}")

    if text and text.strip():
        try:
            # 2. Translate using your existing function
            # Make sure src_lang and dest_lang are the short codes (like 'en', 'hi')
            translated = translate_text(text, src_lang, dest_lang)
            
            # 3. Send back to frontend
            print(f"Success! Translated: {translated}")
            emit('update_result', {'translated_text': translated})
            
        except Exception as e:
            print(f"Translation Error: {e}")
            emit('update_result', {'translated_text': "Error in translation..."})

@app.route("/", methods=["GET", "POST"])

def index():
    translated_text = ""
    original_text = ""
    selected_src = "English"
    selected_dest = "Hindi"

    # Handle Text Translation
    if request.method == "POST" and "translate_text" in request.form:
        original_text = request.form.get("text", "")
        selected_src = request.form.get("src_lang", "English")
        selected_dest = request.form.get("dest_lang", "Hindi")

        if original_text:
            src_code = LANGUAGES.get(selected_src)
            dest_code = LANGUAGES.get(selected_dest)
            # We don't use progress callback for synchronous web requests
            translated_text = translate_text(original_text, src_code, dest_code)

    return render_template(
        "index.html",
        languages=LANGUAGES,
        translated_text=translated_text,
        original_text=original_text,
        selected_src=selected_src,
        selected_dest=selected_dest
    )

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    src_lang = request.form.get("src_lang", "English")
    dest_lang = request.form.get("dest_lang", "Hindi")
    src_code = LANGUAGES.get(src_lang, "en")
    dest_code = LANGUAGES.get(dest_lang, "hi")

    # Save uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Determine file type and read content
    ext = os.path.splitext(filepath)[1].lower()
    content = ""

    try:
        if ext == ".txt":
            content = read_txt(filepath)
        elif ext == ".pdf":
            content = read_pdf(filepath)
        elif ext == ".docx":
            content = read_docx(filepath)
        else:
            return "Unsupported file type. Use .txt, .pdf, or .docx", 400

        # Translate content
        translated_content = translate_text(content, src_code, dest_code)

        # Save and return the translated file
        output_filename = f"{dest_code}-translated-{file.filename}.txt"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        write_txt(output_path, translated_content)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"An error occurred during translation: {str(e)}", 500

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)