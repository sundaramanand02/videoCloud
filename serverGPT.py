# import socket
# import cv2
# import pickle

# # Server configuration
# HOST = '127.0.0.1'  # Server IP
# PORT = 9999  # Port to listen on

# # Initialize socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind((HOST, PORT))
# server_socket.listen(5)

# print("Server listening...")

# # Accept client connection
# client_socket, addr = server_socket.accept()
# print(f"Connection from {addr} has been established.")

# # Receiving frames from client
# frame_count = 0
# while True:
#     frame_data = client_socket.recv(4096)
#     if not frame_data:
#         break
#     frame_count += 1
#     frame = pickle.loads(frame_data)
#     cv2.imshow('Received Frame', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# print(f"Total frames received: {frame_count}")

# # Cleanup
# cv2.destroyAllWindows()
# client_socket.close()
# server_socket.close()



import cv2
import socket
import numpy as np
import struct

internet = bytes()
pointer = 0
    
def recv(size):
    """Simulater socket recv."""
    global pointer

    data = internet[pointer:pointer+size]    
    pointer += size
    
    return data

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

# Wait for a connection
client_socket, addr = server_socket.accept()
print(f'Got connection from {addr}')

# Open a video writer to store the received frames
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter('output.mp4', fourcc, 30, (640, 480))

# Receive and reassemble the frames
ct = 0
while True:
    # Receive the size of the frame data
    size_data = client_socket.recv(4)
    if not size_data:
        break

    # Unpack the size of the frame data
    size = struct.unpack("L", size_data)
    frame_data = client_socket.recv(size)
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

    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
    # frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    video_writer.write(frame)

print("Number of frames: ", ct)
# Release the video writer and close the socket
video_writer.release()
client_socket.close()
server_socket.close()