from flask import Flask, request, session, render_template, g, Response
from camera import VideoCamera
from flask_socketio import SocketIO, emit, send
import cv2
import os

import pickle, socket, struct, threading

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)
app.secret_key = 'secretkey'


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']

        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return render_template('streams.html')
        except IndexError:
            return render_template('index.html')
    return render_template('index.html')


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/video_feed')
def video_feed():
    return ''
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(id=1, username='admin', password='pass')]


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@socketio.on('connect')
def test_connect():
    print("New Connection")
    emit('my response', {'data': 'Connected'})

@socketio.on('msg')
def test_connect(message):
    print("Client messages")
    emit('response msg', "Hello")


if __name__ == '__main__':
    socketio.run(app)

