import cv2
import numpy as np

video = cv2.VideoCapture('file.mp4')

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter('output.mp4', fourcc, 30, (640, 480))

ct = 0
# Read frames from the video
while True:
    ret, frame = video.read()
    if not ret:
        break
    print(type(frame))
    break
    ct += 1
    # Serialize the frame
    serialized_frame = cv2.imencode('.jpg', frame)[1].tobytes()

    # Perform some operations on the serialized frame data
    # For example, you can send it over the network, save it to a database, etc.
    # Here, we are simply reconstructing the frame from the serialized data for demonstration
    reconstructed_frame = cv2.imdecode(np.frombuffer(serialized_frame, dtype=np.uint8), cv2.IMREAD_COLOR)

    video_writer.write(reconstructed_frame)

print("Number of frames: ", ct)

video.release()
video_writer.release()
