from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import os
from datetime import datetime
import sqlite3

from model import model  # YOLOv8 загружается из model.py

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- Инициализация базы данных ----------------

def init_db():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            object_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# ---------------- Главная страница ----------------

@app.route('/')
def index():
    return render_template('index.html')


# ---------------- Обработка изображения ----------------

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['image']
    filename = file.filename.lower()

    image_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    if img is None:
        print("Ошибка декодирования изображения")
        return jsonify({"error": "Невозможно прочитать изображение"}), 400

    # YOLOv8 обработка
    results = model(img)
    output_img = results[0].plot()

    output_path = os.path.join(UPLOAD_FOLDER, 'result.jpg')
    cv2.imwrite(output_path, output_img)

    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO history (timestamp, filename, object_count)
        VALUES (?, ?, ?)
    ''', (datetime.now().isoformat(), filename, len(results[0].boxes)))
    conn.commit()
    conn.close()

    print(f"Объектов найдено: {len(results[0].boxes)}")
    return jsonify(count=len(results[0].boxes))


# ---------------- Точка входа ----------------

if __name__ == '__main__':
    app.run(debug=True)
