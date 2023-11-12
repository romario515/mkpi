from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import Callback
import numpy as np
import os

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Определение директории данных
data_dir = 'dataset'

# Новые размеры входных данных модели после уменьшения
new_image_height = 250
new_image_width = 250

class VisualizationCallback(Callback):
    def __init__(self, validation_data, class_names, output_dir):
        self.validation_data = validation_data
        self.class_names = class_names
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def on_epoch_end(self, epoch, logs=None):
        # Получить случайный набор данных из валидационного генератора
        validation_data = next(self.validation_data)
        x_val, y_val = validation_data[0], validation_data[1]

        # Получить предсказания модели
        predictions = self.model.predict(x_val)

        for i in range(len(predictions)):
            plt.figure(figsize=(2, 2))
            plt.imshow(x_val[i])
            plt.title(f"C_{self.class_names[np.argmax(y_val[i])]} : P_{self.class_names[np.argmax(predictions[i])]}")

            # Сохраняем изображение
            plt.savefig(f"{self.output_dir}/epoch_{epoch+1}_image_{i}.png")
            plt.close()


# Создание генераторов данных
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.0,
    zoom_range=0.2,
    horizontal_flip=False,
    validation_split=0.3  # Для валидационного набора данных
)

# Обучающий генератор данных
train_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(new_image_height, new_image_width),  # Уменьшенный размер изображения
    batch_size=3,  # Вы можете подобрать размер партии в зависимости от доступности памяти
    class_mode='categorical',
    subset='training'
)

# Валидационный генератор данных
validation_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(new_image_height, new_image_width),  # Уменьшенный размер изображения
    batch_size=3,
    class_mode='categorical',
    subset='validation'
)

# Определение модели
#model = Sequential([
#    Conv2D(16, (3, 3), activation='relu', input_shape=(new_image_height, new_image_width, 3)),
#    MaxPooling2D(2, 2),
    # Добавьте дополнительные слои и настройте архитектуру по мере необходимости
#    Flatten(),
#    Dense(512, activation='relu'),
#    Dropout(0.5),
#    Dense(train_generator.num_classes, activation='softmax')
#])



# Компиляция модели
#model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.0001), metrics=['accuracy'])

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(new_image_height, new_image_width, 3)),
    MaxPooling2D(2, 2),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dense(1024, activation='relu'),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation='softmax')
])


# Путь к папке, где будут сохраняться изображения
output_dir = "predictions"
class_names = ['prostoy', 'svarka']
# Создайте экземпляр VisualizationCallback
visualization_callback = VisualizationCallback(validation_generator, class_names, output_dir)


model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.0001), metrics=['accuracy'])

# Обучение модели
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size,
    epochs=45,  # Количество эпох может быть изменено в зависимости от задачи
    callbacks=[visualization_callback]
)

# Сохранение модели
model.save('my_model_250x250_v4.h5')
