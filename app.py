from flask import Flask, render_template, send_from_directory
from flask_pymongo import PyMongo
from flask_socketio import SocketIO, join_room, leave_room
import uuid
import json
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# app.config["MONGO_URI"] = "mongodb://localhost:27017/wavelength"
app.config["MONGO_URI"] = "mongodb+srv://david:today123@cluster0.peg5c.gcp.mongodb.net/wavelength?retryWrites=true&w=majority"
mongo = PyMongo(app)
# socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return 'Homepage :)'

@app.route('/create')
def create():
    return uuid.uuid4().hex[:4], 200

@socketio.on('join_room')
def join_room_and_notify(data):
    room = data['room']
    join_room(room)

    socketio.emit('connection_message', {
        'username': data['username'],
        'photo_url': data['photo_url'],
    }, room)

    room_data = mongo.db.rooms.find_one({
        'token': room
        })

    if not room_data:
       mongo.db.rooms.insert_one({'token': room})
    else:
        messages = room_data['messages']
        socketio.emit('sync_chat', {
            'messages': messages
        }, room)


    socketio.emit('request_timestamp', {
    }, room)

    sync_video_link(data)

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
    room=data['room']
    socketio.emit('update_link', {
        'link': data['link']
    }, room=data['room'])

    mongo.db.rooms.update_one(
        {
            'token': room 
        },
        {
            '$set': {
                'link': data['link']
            }
        },
        upsert=True
    )

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

@socketio.on('sync_video_link')
def sync_video_link(data):
    room = data['room']
    video_link = mongo.db.rooms.find_one({
        'token': room
    })['link']
    socketio.emit('sync_video_link', {
        'link': video_link
    }, room)

@socketio.on('request_timestamp')
def request_timestamp(data):
    socketio.emit('request_timestamp', {})

if __name__ == '__main__':
    socketio.run(app, port=8000)