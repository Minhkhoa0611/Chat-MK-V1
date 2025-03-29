import socket
import threading
from flask import Flask, jsonify, request, render_template
import os
import json
from datetime import datetime
import base64
from flask_cors import CORS

# Ensure Flask finds the correct templates directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Enable CORS for the Flask app
CORS(app)

clients = {}
messages = []
MESSAGE_HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'message_history.json')  # Use the same file as server v1

DATAFILE_DIR = os.path.join(os.path.dirname(__file__), 'datafile_v2')
os.makedirs(DATAFILE_DIR, exist_ok=True)

# List of sensitive keywords to block
SENSITIVE_KEYWORDS = [
    "sex", "18+", "violence", "explicit", "abuse", "gambling", "casino", "bet", "lottery", "poker",
    "porn", "xxx", "adult", "nude", "erotic", "onlyfans", "playboy", "mày", "tao", "đụ", "mẹ", "chửi", "tục", "thô"
]

def contains_sensitive_keywords(text):
    """Check if the text contains any sensitive keywords."""
    return any(keyword in text.lower() for keyword in SENSITIVE_KEYWORDS)

def load_message_history():
    """Load message history from JSON file."""
    if os.path.exists(MESSAGE_HISTORY_FILE):
        with open(MESSAGE_HISTORY_FILE, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return json.loads(content) if content else []
    return []

def save_message_history():
    """Save message history to JSON file."""
    with open(MESSAGE_HISTORY_FILE, 'w') as file:
        json.dump(messages, file, indent=4)

# Load message history on server startup
messages = load_message_history()

@app.before_request
def log_request():
    """Middleware to log all incoming requests."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.remote_addr
    print(f"Date: {timestamp.split(' ')[0]} | Time: {timestamp.split(' ')[1]} | IP: {ip_address}")

@app.route('/')
def index():
    """Main page displaying the user interface."""
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def list_devices():
    """API to list connected devices."""
    return jsonify(list(clients.keys()))

@app.route('/send_request', methods=['POST'])
def send_request():
    """API to send a connection request from one device to another."""
    data = request.json
    sender_id = data.get('sender_id')
    target_id = data.get('target_id')
    if target_id in clients:
        target_socket = clients[target_id]
        target_socket.send(f"REQUEST|{sender_id}".encode())
        return jsonify({"status": "Request sent"})
    return jsonify({"status": "Target not found"}), 404

@app.route('/send_file', methods=['POST'])
def send_file():
    """API to receive and store an image as Base64."""
    data = request.json
    sender_id = data.get('sender_id')
    file_name = data.get('file_name')
    file_data = data.get('file_data')
    if sender_id and file_name and file_data:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_message = {
                'sender_id': sender_id,
                'file_name': file_name,
                'file_data': file_data,
                'timestamp': timestamp
            }
            messages.append(new_message)
            save_message_history()
            return jsonify({"status": "Image saved as Base64"})
        except Exception as e:
            print(f"Error saving image: {e}")
            return jsonify({"status": f"Error: {str(e)}"}), 500
    return jsonify({"status": "Invalid data"}), 400

@app.route('/messages', methods=['GET'])
def get_messages():
    """API to retrieve the list of messages."""
    global messages
    messages = load_message_history()
    return jsonify(messages[-50:])

@app.route('/send_message', methods=['POST'])
def send_message():
    """API to receive and broadcast a message."""
    data = request.json
    sender_id = data.get('sender_id')
    message = data.get('message')
    if sender_id and message:
        if contains_sensitive_keywords(message):
            return jsonify({"status": "Message contains sensitive content and was blocked"}), 400
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_message = {'sender_id': sender_id, 'message': message, 'timestamp': timestamp}
        messages.append(new_message)
        save_message_history()
        return jsonify({"status": "Message sent"})
    return jsonify({"status": "Invalid data"}), 400

@app.route('/send_image', methods=['POST'])
def send_image():
    """API to receive and store an image as Base64."""
    data = request.json
    sender_id = data.get('sender_id')
    image_data = data.get('image_data')
    if sender_id and image_data:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_message = {
                'sender_id': sender_id,
                'image_data': image_data,
                'timestamp': timestamp
            }
            messages.append(new_message)
            save_message_history()
            return jsonify({"status": "Image sent"})
        except Exception as e:
            print(f"Error saving image: {e}")
            return jsonify({"status": f"Error: {str(e)}"}), 500
    return jsonify({"status": "Invalid data"}), 400

def handle_client(client_socket, client_address):
    """Handle connection from a client."""
    try:
        client_id = str(client_address[0])
        clients[client_id] = client_socket
        print(f"Device {client_id} connected from {client_address}")

        client_socket.send(f"ID|{client_id}".encode())

        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        if client_id in clients:
            del clients[client_id]
        client_socket.close()

def start_server(host='0.0.0.0', port=5002):  # Use a different port (5002)
    """Start the server and web interface."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Server started on {host}:{port}")

    threading.Thread(target=lambda: app.run(host='127.0.0.1', port=8003, debug=False)).start()  # Bind Flask to port 8003

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    start_server()
