import time
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os
import cv2

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model and labels
model = load_model("keras_model.h5", compile=False)
class_names = [line.rstrip('\n') for line in open("labels.txt", "r")]

# Define the path to the folder where the images will be stored
folder = "C:\\Users\\kvant\\Desktop\\hacaton_2023\\testing_end_left_right\\"


# Function to process and classify an image
def process_and_classify_image(image):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(image).convert("RGB")

    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the image into the array
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Print prediction and confidence score
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", confidence_score)


# Function to detect motion between two frames
def detect_motion(frame1, frame2):
    # diff = cv2.absdiff(frame1, frame2)
    # gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    # dilated = cv2.dilate(thresh, None, iterations=3)
    # contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # motion_detected = False
    ##
    motion_detected = False
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    # Используйте большее значение для GaussianBlur, чтобы уменьшить шум освещения
    blur = cv2.GaussianBlur(gray, (15, 15), 0)

    # Используйте более высокое пороговое значение для уменьшения чувствительности к мелким изменениям
    _, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)

    # Используйте морфологическую операцию закрытия для удаления маленьких объектов
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours=None
    contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(
            contour)  # преобразование массива из предыдущего этапа в кортеж из четырех координат

        # метод contourArea() по заданным contour точкам, здесь кортежу, вычисляет площадь зафиксированного объекта в каждый момент времени, это можно проверить
        print(cv2.contourArea(contour))

        if cv2.contourArea(contour) < 3000:  # условие при котором площадь выделенного объекта меньше 700 px
            continue
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # получение прямоугольника из точек кортежа
        cv2.putText(frame1, "Status: {}".format("Dvigenie"), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3,
                    cv2.LINE_AA)  # вставляем текст

    # cv2.drawContours(frame1, сontours, -1, (0, 255, 0), 2) также можно было просто нарисовать контур объекта
    ####
    cv2.imshow('Processed Image', frame1)

    for contour in contours:
        if cv2.contourArea(contour) > 3000:  # You can adjust this threshold
            motion_detected = True
            break
    return motion_detected


# Initialize previous image as None
prev_image = None
current_image = None
# Process images from the folder
prev_image_path = ""
while True:
    image_files = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

    for image_file in image_files:
        image_path = os.path.join(folder, image_file)
        current_image = cv2.imread(image_path)

        if prev_image is not None:
            # Detect motion between previous and current image
            if detect_motion(prev_image,current_image ):
                print(f"Motion detected between {prev_image_path} and {image_path}")
            else:
                print(f"No significant motion detected between {prev_image_path} and {image_path}")

        # Process and classify the current image
        if(prev_image_path):
            process_and_classify_image(prev_image_path)

        # Update previous image and path
        prev_image = current_image
        prev_image_path = image_path



        # Display the current image
        #  cv2.imshow('Processed Image', current_image)
        cv2.waitKey(500)  # Display the image for 150 ms
        cv2.destroyAllWindows()

    # Wait for a bit before checking again
    time.sleep(0.5)
