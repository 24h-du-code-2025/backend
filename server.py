import os

import whisper
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from utils import call_agent, convert_mp3_to_wav
from utils.utils_database import database

speech_to_text_model = whisper.load_model("base")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app, cors_allowed_origins='*')

connected_users = []


def convert_mp3_to_wav(mp3_file, wav_file=None):
    """
    Converts an MP3 file to WAV format using ffmpeg.
    
    Args:
        mp3_file (str): Path to the input MP3 file.
        wav_file (str, optional): Path to save the WAV file. 
                                  If None, it saves with the same name as input file.
    
    Returns:
        str: Path to the output WAV file.
    """
    if wav_file is None:
        wav_file = mp3_file.replace(".mp3", ".wav")

    try:
        # Use ffmpeg to convert MP3 to WAV
        ffmpeg.input(mp3_file).output(wav_file, format='wav').run(overwrite_output=True, quiet=True)
        return wav_file
    except Exception as e:
        print(f"Error converting {mp3_file} to WAV: {e}")
        return None


@app.post("/convert-speech-to-text")
def convert_speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files['audio']

    # if not audio_file.filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
    #     return jsonify({"error": "Invalid file format. Please upload an MP3, WAV, M4A, or OGG file."}), 400

    temp_audio_path = f"temp_{audio_file.filename}"
    audio_file.save(temp_audio_path)

    if temp_audio_path.endswith('.mp3'):
        temp_audio_path = convert_mp3_to_wav(temp_audio_path)

    try:
        result = speech_to_text_model.transcribe(temp_audio_path, language="fr")
        print(temp_audio_path)
        os.remove(temp_audio_path)  # Clean up temporary file
        return jsonify({"text": result["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sio.on('chat')
def handle_chat(data):
    session = database.sessions.find_one({"sid": request.sid})

    if "message" not in data:
        return

    add_message("user", data["message"])
    call_agent(data["message"], session)


@sio.on('connect')
def handle_connect(auth=None):
    if auth is None or "token" not in auth:
        return
    session = database.sessions.find_one({"token": auth["token"]})
    if session is None:
        database.sessions.insert_one({"token": auth["token"], "history": []})
        session = database.sessions.find_one({"token": auth["token"]})

    session["sid"] = request.sid
    update_session(session)
    send_history(session)


def add_message(from_name, content):
    session = database.sessions.find_one({"sid": request.sid})
    session["history"].append({
        "from": from_name,
        "type": "message",
        "content": content
    })
    update_session(session)
    send_history(session)


def add_structured_message(message_type, content):
    session = database.sessions.find_one({"sid": request.sid})
    session["history"].append({
        "from": "agent",
        "type": message_type,
        "content": content
    })
    update_session(session)
    send_history(session)


def update_session(session):
    database["sessions"].update_one({"_id": session["_id"]}, {"$set": session})


def send_history(session):
    emit('update_history', session["history"], to=session["sid"])


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
