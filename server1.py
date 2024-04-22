import cv2
import socket
import numpy as np
import struct 
import json

from cryptography.fernet import Fernet


def motion_compensation_and_error(reference_frame, motion_vectors, error_frame, block_size):
    """Reconstructs a frame by applying motion vectors to a reference frame.

    Args:
        reference_frame: The reference frame as a NumPy array.
        motion_vectors: A list of motion vectors, where each vector is a tuple of (x, y, dx, dy).
        block_size: The size of the blocks to which the motion vectors apply.

    Returns:
        The reconstructed frame as a NumPy array.
    """
    height, width = reference_frame.shape[:2]
    reconstructed_frame = np.zeros_like(reference_frame)

    for x, y, dx, dy in motion_vectors:
        block = reference_frame[y+dy:y+dy+block_size, x+dx:x+dx+block_size]
        reconstructed_frame[y:y+block_size, x:x+block_size] = block

    reconstructed_frame = reconstructed_frame + error_frame
    return reconstructed_frame

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
block_size = 64
ct = 0
 


size_data = client_socket.recv(16) 
size, width, height, depth = struct.unpack('LIII', size_data) 
print(size) 
    
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
frame_dec = decrypt_npy_file(frame_data)
ct += 1 
frame_array = np.frombuffer(frame_dec, dtype=np.uint8).reshape((width, height, depth)) 
video_writer.write(frame_array)

prev_frame=cv2.cvtColor(frame_array, cv2.COLOR_BGR2RGB)

while True:
    # Receive the size of the frame data
    size_data = client_socket.recv(12)
    if not size_data:
        break
    # print(type(size_data))
    # print(size_data)
    # print(type(size_data))
    # Unpack the size of the frame data
    size, width, height = struct.unpack('III', size_data)
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

    frame_array = np.frombuffer(frame_dec, dtype=np.uint8).reshape((width, height))

###



    size_data_mv = client_socket.recv(12)
    if not size_data_mv:
        break 
    size_mv, width_mv, height_mv = struct.unpack('III', size_data_mv)
    # print(type(size))
    print("size_mv",size_mv)
    # print(type(size))
    
    received_data_mv = b''
    rs_mv = 0
    while rs_mv < size_mv:
        rem_sz_mv = size_mv - rs_mv
        data_mv = client_socket.recv(min(rem_sz_mv, 4096))
        if not data_mv:
            break
        received_data_mv += data_mv
        rs_mv += len(data_mv)
    frame_data_mv = received_data_mv 
    frame_dec_mv = decrypt_npy_file(frame_data_mv)
    ct += 1 

    frame_array_mv = np.frombuffer(frame_dec_mv, dtype=np.uint8).reshape((width_mv, height_mv))
    
    motion_vectors_list = frame_array_mv.tolist()



###


    reconstructed_frame = motion_compensation_and_error(prev_frame, motion_vectors_list, frame_array, block_size)

    prev_frame = reconstructed_frame
    reconstructed_frame = cv2.cvtColor(reconstructed_frame, cv2.COLOR_RGB2BGR)
    # fframe = cv2.cvtColor(frame_array, cv2.COLOR_GRAY2BGR)
    video_writer.write(reconstructed_frame)
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