# import socket
# import cv2
# import pickle

# # Client configuration
# HOST = '127.0.0.1'  # Server IP
# PORT = 9999  # Port to connect

# # Initialize socket
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((HOST, PORT))

# # Video capture
# video_path = 'file.mp4'  # Path to video file
# video_capture = cv2.VideoCapture(video_path)

# # Sending frames to server
# while True:
#     ret, frame = video_capture.read()
#     if not ret:
#         break
#     frame_data = pickle.dumps(frame)
#     client_socket.sendall(frame_data)

# # Cleanup
# video_capture.release()
# client_socket.close()



import cv2
import socket
import struct

internet = bytes()
pointer = 0
def send(data):
    """Simulater socket send."""
    global internet
    
    internet += data

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 12345

# Connect to the server
client_socket.connect((host, port))

# Open the video file
video = cv2.VideoCapture('file.mp4')

ct = 0
# Read frames from the video
while True:
    ret, frame = video.read()
    if not ret:
        break

    ct += 1
    # Serialize the frame
    serialized_frame = frame.tobytes()

    # Send the size of the frame data first
    size = len(serialized_frame)
    
    # width, height, depth = frame.shape
    # byte_width_height = struct.pack('III', width, height, depth)
    client_socket.sendall(struct.pack("L", size) + serialized_frame)

    # Send the frame data
    # client_socket.sendall(serialized_frame)

print("Number of frames: ", ct)
# Close the video file and socket
video.release()
client_socket.close()