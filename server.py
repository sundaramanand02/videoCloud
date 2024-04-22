import cv2
import socket
import numpy as np
import struct

from cryptography.fernet import Fernet

def decrypt_npy_file(encrypted_data):
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()
    cipher = Fernet(key)

    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 12345

# Bind the socket to the host and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)

print(f'Server listening on {host}:{port}')

fourcc = cv2.VideoWriter_fourcc(*'avc1')
video_writer = cv2.VideoWriter('output.mp4', fourcc, 30.0, (852, 480))

client_socket, addr = server_socket.accept()
print(f'Got connection from {addr}')

motion_vector_final = []
ct = 0
while True:
    # Receive the size of the frame data
    size_data = client_socket.recv(16)
    if not size_data:
        break
    # print(type(size_data))
    # print(size_data)
    # print(type(size_data))
    # Unpack the size of the frame data
    size, width, height, depth = struct.unpack('LIII', size_data)
    # print(type(size))
    print(size)
    # print(type(size))
    
    received_data = b''
    rs = 0
    while rs < size:
        rem_sz = size - rs
        data = client_socket.recv(min(rem_sz, 4096))
        if not data:
            break
        received_data += data
        rs += len(data)
    frame_data = received_data

    # frame_data = client_socket.recv(size)
    # client_socket.send(b'h')
    # print(ct, end=" ")
    # print(len(frame_data))
    # print("he")
    # print(ct, len(frame_data))
    frame_dec = decrypt_npy_file(frame_data)
    ct += 1
    # Receive the frame data
    # frame_data = b''
    # remaining = size
    # while remaining:
    #     chunk = client_socket.recv(min(remaining, 1024 * 1024))
    #     if not chunk:
    #         break
    #     frame_data += chunk
    #     remaining -= len(chunk)

    frame_array = np.frombuffer(frame_dec, dtype=np.uint8).reshape((width, height, depth))
    # fframe = cv2.cvtColor(frame_array, cv2.COLOR_GRAY2BGR)
    video_writer.write(frame_array)
    # print(len(frame_array))
    # cv2.imwrite('after_image.jpg', frame_array)
    # np.save("after1.npy", frame_array)
    # motion_vector_final.append(frame_array)
    # frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    

# np.save("after.npy", motion_vector_final)
print("Received frames: ", ct)
video_writer.release()
client_socket.close()
server_socket.close()