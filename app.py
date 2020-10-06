from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, join_room, leave_room
import uuid
import json
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config["MONGO_URI"] = "mongodb://localhost:27017/wavelength"
mongo = PyMongo(app)
# socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/create')
def create():
    return uuid.uuid4().hex[:4], 200

@socketio.on('connect')
def connection():
    print('connected')

@socketio.on('join_room')
def join_room_and_notify(data):
    room = data['room']
    join_room(room)

    socketio.emit('connection_message', {
        'username': data['username'],
        'photo_url': data['photo_url'],
    }, room)

    messages = mongo.db.rooms.find_one({
        'token': room
        })['messages']
    socketio.emit('sync_chat', {
        'messages': messages
    }, room)

    socketio.emit('request_timestamp', {
    }, room)


@socketio.on('chat_message')
def handle_message(data):
    username = data['username'] 
    photo_url = data['photo_url']
    message = data['message']
    room = data['room']

    mongo.db.rooms.update_one(
        {
            'token': room 
        },
        {
            '$push': {
                'messages': data
            }
        },
        upsert=True
    )

    socketio.emit('chat_message', {
        'username': username,
        'photo_url': photo_url,
        'message': message
    }, room=room)

@socketio.on('update_link')
def update_link(data):
    socketio.emit('update_link', {
        'link': data['link']
    }, room=data['room'])

@socketio.on('play_video')
def play_all(data):
    socketio.emit('play_video', {
        'timestamp': data['timestamp'],
        'actionStamp': datetime.datetime.now().timestamp()*1000
    }, room=data['room'])

@socketio.on('pause_video')
def pause_all(data):
    socketio.emit('pause_video', {
    }, room=data['room'])

@socketio.on('update_timestamp')
def set_timestamp(data):
    socketio.emit('sync_timestamp', {
        'timestamp': data['timestamp']
    }, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, port=8000)