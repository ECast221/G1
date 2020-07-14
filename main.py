from flask import Flask, request, session, render_template, g
from camera import VideoCamera
import cv2
import os

import pickle, socket, struct, threading


app = Flask(__name__, static_folder='static')
app.secret_key = 'secretkey'
backupCam = VideoCamera()
videoFrame = backupCam.get_frame()
connected = False
PORT = int(os.environ.get('PORT'))


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


def socket_listener():
    global videoFrame, connected
    HOST = '0.0.0.0'
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    s.bind((HOST, PORT))
    print('Socket bind complete')
    while True:
        connected = False
        s.listen(10)
        print('Socket now listening')
        conn, addr = s.accept()
        with conn:
            connected = True
            print('Connected by', addr)
            data = b''
            payload_size = struct.calcsize("L")  # CHANGED


            while connected:
                try:
                    # Retrieve message size
                    while len(data) < payload_size:
                        data += conn.recv(4096)

                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("L", packed_msg_size)[0]  # CHANGED

                    # Retrieve all data based on message size
                    while len(data) < msg_size:
                        data += conn.recv(4096)

                    frame_data = data[:msg_size]
                    data = data[msg_size:]

                    # Extract frame
                    frame = pickle.loads(frame_data)
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    videoFrame = jpeg.tobytes()
                except socket.error:
                    connected = False
                    videoFrame = backupCam.get_frame()
                    print("client disconnected")

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


@app.route('/video_feed')
def video_feed():
    return ''
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')



class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = [User(id=1, username='admin', password='pass')]


def gen():
    while True:
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + videoFrame + b'\r\n\r\n')


if __name__ == '__main__':
    t = threading.Thread(target=socket_listener, args=())
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=PORT)
