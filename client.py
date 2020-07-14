import cv2
import numpy as np
import socket
import sys
import pickle
import struct
import time

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Use the following:  ((LOCAL_IP_ADDRESS, SERVER_PORT)) FOR LOCAL
clientSocket.connect(('10.0.0.30', 8089))                   # LOCAL STREAM
# Use the following:  ((HEROKU_ADDRESS, 80 (?) )) FOR HEROKU CONNECTION
# clientSocket.connect(('cnt-ecv3.herokuapp.com', 80))      # HEROKU CONNECT


while True:
    ret, frame = cap.read()
            # Serialize frame
    data = pickle.dumps(frame)

            # Send message length first
    message_size = struct.pack("L", len(data))
    print(len(data))
            # Then data
    clientSocket.sendall(message_size + data)
