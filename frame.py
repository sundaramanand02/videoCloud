import numpy as np
import cv2


fourcc = cv2.VideoWriter_fourcc(*'avc1')
video_writer = cv2.VideoWriter('output111.mp4', fourcc, 30.0, (852, 480))

ct = 0
video_path = 'file.mp4'
cap = cv2.VideoCapture(video_path)
prev_frame = []
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # if len(prev_frame) == 0:
    #     prev_frame = gray_frame
        # continue
    # cv2.imwrite('before_image.jpg', frame)
    # print(frame.shape)
    # rebuilt_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

    np_data = np.array(frame)
    serialized_data = np_data.tobytes()
    ct += 1
    frame_array = np.frombuffer(serialized_data, dtype=np.uint8).reshape(frame.shape)
    video_writer.write(frame_array)
    # cv2.imwrite('after_image.jpg', frame_array)

    # out.write(output_frame)
    # motion_vec_final.append(motion_vec)
    # break

# np.save("before.npy", motion_vector_final)
cap.release()
video_writer.release()
# out.release()
cv2.destroyAllWindows()
print("Sent frames: ", ct)