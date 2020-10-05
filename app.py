from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def connection():
    print('connected')

@socketio.on('join_room')
def join_room_and_notify(data):
    room = data['room']
    print('join_room requested')
    join_room(room)

    socketio.emit('connection_message', {
        'username': data['username'],
        'photo_url': data['photo_url'],
    }, room)

@socketio.on('chat_message')
def handle_message(data):
    socketio.emit('chat_message', {
        'username': data['username'],
        'photo_url': data['photo_url'],
        'message': data['message']
    })

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@app.route('/create')
def create():
    return uuid.uuid4().hex[:4], 200

if __name__ == '__main__':
    socketio.run(app, port=2000)