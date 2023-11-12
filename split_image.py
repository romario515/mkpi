from PIL import Image
import os
import time


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")


def split_and_delete_images_in_folder(folder_path, left_folder, right_folder):
    # Проверяем и создаем папки, если необходимо
    create_folder_if_not_exists(folder_path)
    create_folder_if_not_exists(left_folder)
    create_folder_if_not_exists(right_folder)

    while True:  # Бесконечный цикл для непрерывной проверки наличия новых изображений
        # Список всех файлов изображений в папке
        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]

        if not image_files:  # Если изображения отсутствуют, ожидаем
            time.sleep(5)  # Проверяем наличие новых изображений каждые 5 секунд
            continue

        for image_file in image_files:
            # Полный путь к изображению
            image_path = os.path.join(folder_path, image_file)

            # Загружаем изображение
            img = Image.open(image_path)

            # Делим изображение на две части
            left_half = img.crop((68, 229, 737, 898))  # 670
            right_half = img.crop((1116, 229, 1785, 898))  # 670

            # Сохраняем две части
            left_half.save(os.path.join(left_folder, f'left_{image_file}'))
            right_half.save(os.path.join(right_folder, f'right_{image_file}'))

            # Удаляем исходное изображение после обработки
            os.remove(image_path)
            #print(f"Processed and deleted {image_file}")

        # Ждем некоторое время перед следующей проверкой
        time.sleep(5)


# Пути к папкам
folder_path = 'mkpi-frames'
left_folder = 'mkpi-frames_split\\'
right_folder = 'mkpi-frames_split\\'

# Запуск функции
split_and_delete_images_in_folder(folder_path, left_folder, right_folder)
