import numpy as np
import cv2
import socket
import struct
from cryptography.fernet import Fernet

def block_matching(frame1, frame2, block_size, search_range):
  """Performs block matching between two frames.
    frame1: The first frame as a NumPy array.
    frame2: The second frame as a NumPy array.
    block_size: The size of the blocks to match.
    search_range: The maximum displacement to search for matching blocks.

    Returns a list of motion vectors, where each vector is a tuple of (x_displacement, y_displacement).
  """

  height, width = frame1.shape[:2]
  motion_vectors = []

  for y in range(0, height - block_size, block_size):
    for x in range(0, width - block_size, block_size):
      block1 = frame1[y:y+block_size, x:x+block_size]

      best_match = None
      min_error = np.inf

      for dy in range(-search_range, search_range + 1):
        for dx in range(-search_range, search_range + 1):
          y2 = y + dy
          x2 = x + dx

          if 0 <= y2 < height - block_size and 0 <= x2 < width - block_size:
            block2 = frame2[y2:y2+block_size, x2:x2+block_size]
            error = np.sum((block1 - block2)**2) / (block_size**2)  # MSE
            if error < min_error:
              min_error = error
              best_match = (dx, dy)

      motion_vectors.append([x, y, best_match[0], best_match[1]])

  return motion_vectors

def generate_key():
    key = Fernet.generate_key()

    with open('filekey.key', 'wb') as filekey:
        filekey.write(key)

def encrypt_npy_file(data):
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()
    cipher = Fernet(key)
    # data = np.load(input_file_path)
    np_data = np.array(data)
    serialized_data = np_data.tobytes()
    encrypted_data = cipher.encrypt(serialized_data)

    return encrypted_data


# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 12345

# Connect to the server
client_socket.connect((host, port))

generate_key()

motion_vector_final = []
video_path = 'file.mp4'
cap = cv2.VideoCapture(video_path)
# print((int(cap.get(3)), int(cap.get(4))))
# fps = cap.get(cv2.CAP_PROP_FPS)
# print("Frames per second (fps) of the video:", fps)
# codec = int(cap.get(cv2.CAP_PROP_FOURCC))
# codec_str = ''.join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
# print("Codec of the video:", codec_str)

# motion_vec_final = []
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# output_path = 'motion_estimation.mp4'
# out = cv2.VideoWriter(output_path, fourcc, 30, (int(cap.get(3)), int(cap.get(4))))
ct = 0
block_size = 64  # Size of the block for motion estimation
max_displacement = 8  # Maximum displacement to search within
prev_frame = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if len(prev_frame) == 0:
        prev_frame = gray_frame
        continue
    # cv2.imwrite('before_image.jpg', frame)
    print(len(frame))
    # motion_vec = block_matching(prev_frame, gray_frame, block_size, max_displacement)
    # motion_vector_final.append(motion_vec)
    # encrypted_data = encrypt_npy_file(motion_vec, key)
    # size = len(encrypted_data)
    # print(size)
    # width, height, depth = frame.shape
    # byte_width_height = struct.pack('III', width, height, depth)
    # client_socket.sendall(struct.pack("L", size) + encrypted_data)

    encrypted_frame = encrypt_npy_file(frame)
    frame_size = len(encrypted_frame)
    print(ct, frame_size)
    width, height, depth = frame.shape
    byte_width_height = struct.pack('LIII', frame_size, width, height, depth)
    # print(len(byte_width_height))
    client_socket.sendall(byte_width_height + encrypted_frame)
    # f = client_socket.recv(1)
    # np.save("before1.npy", frame)
    ct += 1
    # motion_vec_final.append(motion_vec)

    # out.write(output_frame)
    # motion_vec_final.append(motion_vec)
    # break

# np.save("before.npy", motion_vector_final)
cap.release()
# out.release()
cv2.destroyAllWindows()
print("Sent frames: ", ct)