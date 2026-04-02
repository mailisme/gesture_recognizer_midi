import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision
from mediapipe.tasks import python
import time
import mido
from mido import Message

# code edit from:
# https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/gesture_recognizer/python/gesture_recognizer.ipynb
# https://colab.research.google.com/github/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb
mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result, category):
  hand_landmarks_list = detection_result
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]

    # Draw the hand landmarks.
    mp_drawing.draw_landmarks(
      annotated_image,
      hand_landmarks,
      mp_hands.HAND_CONNECTIONS,
      mp_drawing_styles.get_default_hand_landmarks_style(),
      mp_drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{category.category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image

outport = mido.open_output('loopMIDI Port 10')

note = 0
def midi_out(status):
    global note
    if status == 0:
        print("note off")
        outport.send(msg=Message('note_off', note=note, velocity=100))
    else:
        for idx in [12, 14, 60, 62]:
            if status == idx:
                if note == 0:

                    outport.send(msg=Message('note_on', note=idx, velocity=100))
                    print(idx)
                    note = idx
                    return
                elif note == idx:
                    print(idx)
                    note = idx
                    return
                else:

                    outport.send(msg= Message('note_off',note=note, velocity=100))
                    outport.send(msg=Message('note_on', note=idx, velocity=100))
                    print(idx)
                    note = idx
                    return




base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
options = vision.GestureRecognizerOptions(base_options=base_options)

recognizer = vision.GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    recognition_result = recognizer.recognize(mp_image)
    if recognition_result.gestures:
        top_gesture = recognition_result.gestures[0][0]
        hand_landmarks = recognition_result.hand_landmarks

        print((top_gesture, hand_landmarks))

        annotated_image = draw_landmarks_on_image(rgb_image=rgb, detection_result=hand_landmarks, category=top_gesture)

        if top_gesture.category_name == 'Open_Palm':
            midi_out(60)
        elif top_gesture.category_name == 'Closed_Fist':
            midi_out(12)
        elif top_gesture.category_name == 'Thumb_Up':
            midi_out(62)
        elif top_gesture.category_name == 'Thumb_Down':
            midi_out(14)
        else:
            midi_out(0)
        cv2.imshow("video", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    else:
        cv2.imshow("video", frame)
        midi_out(0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()