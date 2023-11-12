import subprocess
import os
import sqlite3
import time

def ensure_table_exists(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_videos (
        video_name TEXT PRIMARY KEY
    )
    """)
    db_connection.commit()

def is_video_processed(db_connection, video_name):
    cursor = db_connection.cursor()
    cursor.execute("SELECT 1 FROM processed_videos WHERE video_name = ?", (video_name,))
    return cursor.fetchone() is not None

def extract_frames_gpu(video_path, target_folder, frame_rate=1):
    video_name = os.path.basename(video_path)
    dop_name = os.path.join(target_folder, os.path.splitext(video_name)[0])



    ffmpeg_cmd = [
        'ffmpeg',  # Укажите полный путь к ffmpeg, если он не в PATH
        '-hwaccel', 'cuda',
        '-i', video_path,
        '-r', str(frame_rate),
        os.path.join(target_folder, f"{os.path.splitext(video_name)[0]}_frame_%04d.jpg")
    ]

    subprocess.run(ffmpeg_cmd)
    print(f"Кадры успешно извлечены и сохранены в {target_folder}")

db_connection = sqlite3.connect('mkpi.db')
ensure_table_exists(db_connection)

video_folder = 'mkpi-videos\\'
target_folder = 'mkpi-frames\\'

processed_videos = set()  # Для хранения уже обработанных видео

while True:  # Бесконечный цикл для непрерывного мониторинга
    for video_file in os.listdir(video_folder):
        if video_file.endswith(('.mp4', '.avi', '.mov')) and video_file not in processed_videos:
            video_path = os.path.join(video_folder, video_file)

            if not is_video_processed(db_connection, video_file):
                extract_frames_gpu(video_path, target_folder, 1)
                cursor = db_connection.cursor()
                cursor.execute("INSERT INTO processed_videos (video_name) VALUES (?)", (video_file,))
                db_connection.commit()
                processed_videos.add(video_file)

    time.sleep(10)  # Ожидание 10 секунд перед следующей проверкой

# Не забудьте закрыть соединение с БД, когда оно вам больше не понадобится
# db_connection.close()
