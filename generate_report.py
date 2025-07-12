import sqlite3
from openpyxl import Workbook
from datetime import datetime

def generate_excel_report():
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history')
    rows = cursor.fetchall()
    conn.close()

    wb = Workbook()
    ws = wb.active
    ws.title = "Учёт объектов"

    ws.append(['ID', 'Дата и время', 'Имя файла', 'Обнаружено объектов'])

    for row in rows:
        ws.append(row)

    filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)
    print(f"Отчёт сохранён в файл: {filename}")

generate_excel_report()
