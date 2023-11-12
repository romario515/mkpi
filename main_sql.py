import time
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os
import cv2
import re
from datetime import datetime
import sqlite3


def ensure_table_exists(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pos_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pos_name TEXT,
        status TEXT,
        video_name TEXT,
        timeserver TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        t_fst TIME
    )
    """)
    db_connection.commit()
    cursor.execute("""
	CREATE TABLE IF NOT EXISTS admins (
		id      INTEGER PRIMARY KEY AUTOINCREMENT,
		chat_id TEXT    NOT NULL
	)
    """)
    db_connection.commit()
    cursor.execute("""
	CREATE TABLE IF NOT EXISTS admins (
		id      INTEGER PRIMARY KEY AUTOINCREMENT,
		chat_id TEXT    NOT NULL
	)
    """)
    db_connection.commit()


def insert_into_db(db_connection, pos_name, video_name, t_fst, status,timeserver):
    # Предполагается, что функция times возвращает кортеж из двух элементов: timeserver и t_fst


    cursor = db_connection.cursor()
    cursor.execute("""
        INSERT INTO pos_history (pos_name, status, video_name, timeserver, t_fst)
        VALUES (?, ?, ?, ?, ?)
    """, (pos_name, status, video_name, timeserver, t_fst))

    db_connection.commit()


# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model and labels
model = load_model("224X224.h5", compile=False)
class_names = [line.rstrip('\n') for line in open("labels.txt", "r")]

# Define the path to the folder where the images will be stored
folder = "mkpi-frames_split\\"


# Function to process and classify an image
def process_and_classify_image(image):
    #print(model.classes)

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(image).convert("RGB")

    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # turn the image into a numpy array
    image_array = np.asarray(image)
    #print(image_array)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the image into the array
    data[0] = normalized_image_array
    #print(data)
    # Predicts the model
    prediction = model.predict(data)
    #print(prediction)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Print prediction and confidence score

    #print("Class:", class_name, end="")
    #print("Confidence Score:", confidence_score)
    #print()
    return class_name[2:]


def times(t_fst):
    # Получение текущего времени в формате timestamp для SQLite
    current_timestamp = int(time.time())

    # Вывод текущего времени в формате timestamp
    #print("Current Timestamp for SQLite:", current_timestamp)

    # Конвертация секунд в форматированное время (часы:минуты:секунды)
    #print(t_fst)
    seconds = t_fst  # Пример секунд, которые нужно конвертировать
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = int(seconds) % 60

    # Вывод времени в формате ЧЧ:ММ:СС
    time_format = f"{hours:02}:{minutes:02}:{seconds:02}"
    #print("Time from seconds:", time_format)

    # Для использования в SQLite в формате ISO 8601
    current_time_for_sqlite = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print("Current Time for SQLite:", current_time_for_sqlite)

    return [time_format, current_time_for_sqlite]


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
    if frame1 is None or frame2 is None:
        return "Error"

    # Check if frames have the same dimensions
    if frame1.shape != frame2.shape:
        return "Error"

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
        ####
        # метод contourArea() по заданным contour точкам, здесь кортежу, вычисляет площадь зафиксированного объекта в каждый момент времени, это можно проверить
        #print(cv2.contourArea(contour))

        if cv2.contourArea(contour) < 3000:  # условие при котором площадь выделенного объекта меньше 700 px
           continue
        #cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)  # получение прямоугольника из точек кортежа
        #cv2.putText(frame1, "Status: {}".format("Dvigenie"), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3,
        #cv2.LINE_AA)  # вставляем текст

    #cv2.drawContours(frame1, contours, -1, (0, 255, 0), 2) #также можно было просто нарисовать контур объекта

    #cv2.imshow('Processed Image', frame1)

    ####
    #ПЛОЩАДЬ квадратика
    for contour in contours:
        if cv2.contourArea(contour) > 3000:  # You can adjust this threshold
            motion_detected = True
            #print("НАААААААШЛИ")
            break
    return motion_detected


# Initialize previous image as None
prev_image = None
current_image = None
# Process images from the folder
prev_image_path = ""

db_connection = sqlite3.connect('mkpi.db')
ensure_table_exists(db_connection)

while True:
    image_files = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

    for image_file in image_files:
        image_path = os.path.join(folder, image_file)
        current_image = cv2.imread(image_path)
        old_status = ""
        if prev_image is not None:
            # Detect motion between previous and current image
            if detect_motion(prev_image, current_image):
                #print("detected")
                old_status = "Detect"

        status = ""
        # Process and classify the current image
        if (prev_image_path):
            #print("testim")
            print(prev_image_path)
            status = process_and_classify_image(prev_image_path)
            if (status != 'svarka') and (old_status != ""):
                #print("VUNUS")
                status = "vinuzhdennaya"

        #print(prev_image_path)
        # Ваш путь к файлу

        # Регулярное выражение для поиска совпадений
        # Оно находит любое слово до первого подчеркивания, затем имя видео до '_frame_', и номер кадра после '_frame_'
        pattern = r"(\w+?)_(.+)_frame_(\d+)\.jpg"
        match = re.match(pattern, os.path.split(prev_image_path)[1])
        #print(status)
        #print()
        if match:
            pos_name = match.group(1)  # 'left'
            video_name = match.group(2)  # '8m_video'
            frame_time = match.group(3)  # '0007' предполагается, что это время кадра в формате hh:mm:ss или другом
            #print(f"Position name: {pos_name}")
            #print(f"Video name: {video_name}")
            #print(f"Frame time: {frame_time}")

        if match:
            pos_name = match.group(1)  # Слово до первого подчеркивания
            video_name = match.group(2)  # Имя видео
            frame_number = match.group(3)  # Номер кадра

            frame_number = times(frame_number)  # возвращает массив с двумя значениями для timeserver и t_fst
            # Пример использования функции
            db_connection = sqlite3.connect('mkpi.db')

            # Вызовите функцию insert_into_db с соответствующими значениями
            insert_into_db(db_connection, pos_name, video_name, frame_number[0], status,frame_number[1])

        # Update previous image and path
        if(prev_image_path):
            os.remove(prev_image_path)
        prev_image = current_image
        prev_image_path = image_path

        # Display the current image
        #  cv2.imshow('Processed Image', current_image)
        #СКОЛЬКО КВАДРАТИК ВИСИТ
        cv2.waitKey(1500)  # Display the image for 150 ms
        cv2.destroyAllWindows()

    # Wait for a bit before checking again
    time.sleep(10)
