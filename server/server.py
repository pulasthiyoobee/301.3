# server/server.py
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import bcrypt
from database import init_db
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
clients = {}  # Dictionary to keep track of connected clients

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    public_key = data['public_key']

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, public_key) VALUES (?, ?, ?)', (username, hashed_password, public_key))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'User registered successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Username already exists'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})

@app.route('/get_public_key', methods=['POST'])
def get_public_key():
    data = request.get_json()
    username = data['username']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT public_key FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'public_key': user[0]})
    else:
        return jsonify({'status': 'error', 'message': 'User not found'})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    for username, sid in clients.items():
        if sid == request.sid:
            del clients[username]
            break

@socketio.on('register_user')
def register_user(data):
    username = data['username']
    clients[username] = request.sid

@socketio.on('message')
def handle_message(data):
    recipient = data['recipient']
    message = data['message']
    sender = None

    for username, sid in clients.items():
        if sid == request.sid:
            sender = username
            break

    if recipient in clients:
        recipient_sid = clients[recipient]
        emit('message', {'sender': sender, 'message': message}, room=recipient_sid)
    else:
        print(f'User {recipient} not connected')

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
