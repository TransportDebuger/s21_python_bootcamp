import threading
import queue
import time
import random
import math
import os
from sys import exit

# Инициализация поддержки ANSI-кодов для Windows
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# Глобальные переменные
students = []
examiners = []
questions = []
student_lock = threading.Lock()
examiner_lock = threading.Lock()
start_time = time.time()
print_lock = threading.Lock()

class Student:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.status = "Очередь"
        self.exam_time = None
        self.answers = []

class Examiner:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.current_student = None
        self.total = 0
        self.failed = 0
        self.work_time = 0.0
        self.on_lunch = False

def read_files():
    try:
        # Чтение экзаменаторов
        with open("examiners.txt", "r", encoding='utf-8') as f:
            examiners_data = []
            for line in f:
                line = line.strip()
                if line:
                    examiners_data.extend(line.split())
            
            if len(examiners_data) % 2 != 0:
                raise ValueError("Некорректный формат файла examiners.txt")
            
            for i in range(0, len(examiners_data), 2):
                name = examiners_data[i]
                gender = examiners_data[i+1]
                if gender not in ('М', 'Ж'):
                    raise ValueError(f"Некорректный пол у экзаменатора {name}")
                examiners.append(Examiner(name, gender))
        
        # Чтение студентов
        with open("students.txt", "r", encoding='utf-8') as f:
            students_data = []
            for line in f:
                line = line.strip()
                if line:
                    students_data.extend(line.split())
            
            if len(students_data) % 2 != 0:
                raise ValueError("Некорректный формат файла students.txt")
            
            for i in range(0, len(students_data), 2):
                name = students_data[i]
                gender = students_data[i+1]
                if gender not in ('М', 'Ж'):
                    raise ValueError(f"Некорректный пол у студента {name}")
                students.append(Student(name, gender))
        
        # Чтение вопросов
        with open("questions.txt", "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    questions.append(line)
                    
    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e.filename}")
        exit(1)
    except ValueError as e:
        print(f"Ошибка формата данных: {e}")
        exit(1)
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        exit(1)

def draw_table(headers, data):
    if not data:
        return ""
    
    # Рассчитываем ширину колонок
    col_widths = [
        max(len(str(row[i])) for row in data + [headers])
        for i in range(len(headers))
    ]
    
    # Создаем шапку таблицы
    header = "|".join(f" {h.ljust(w)} " for h, w in zip(headers, col_widths))
    separator = "+".join("-" * (w + 2) for w in col_widths)
    rows = []
    
    # Добавляем данные
    for row in data:
        rows.append("|".join(
            f" {str(cell).ljust(w)} " 
            for cell, w in zip(row, col_widths)
        ))
    
    return (
        f"+{separator}+\n"
        f"|{header}|\n"
        f"+{separator}+\n"
        + "\n".join(f"|{r}|" for r in rows) + 
        f"\n+{separator}+"
    )

def update_display():
    prev_lines = 0
    while True:
        with print_lock:
            buffer = []
            
            # Собираем данные студентов
            with student_lock:
                sorted_students = sorted(students, key=lambda x: ["Очередь", "Сдал", "Провалил"].index(x.status))
                student_data = [[s.name, s.status] for s in sorted_students]
            
            buffer.append(draw_table(["Студент", "Статус"], student_data))
            
            # Собираем данные экзаменаторов
            examiner_data = []
            with examiner_lock:
                for e in examiners:
                    current = e.current_student.name if e.current_student else "-"
                    examiner_data.append([
                        e.name,
                        current,
                        str(e.total),
                        str(e.failed),
                        f"{e.work_time:.2f}"
                    ])
            
            buffer.append("\n" + draw_table(
                ["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"],
                examiner_data
            ))
            
            # Считаем оставшихся студентов
            with student_lock:
                remaining = sum(1 for s in students if s.status == "Очередь")
                total = len(students)
            
            buffer.append(f"\nОсталось в очереди: {remaining} из {total}")
            buffer.append(f"Время с момента начала экзамена: {time.time() - start_time:.2f}")
            
            # Формируем вывод
            output = "\n".join(buffer)
            clear = f"\033[{prev_lines}F\033[J"
            print(f"{clear}{output}", end="", flush=True)
            prev_lines = output.count('\n') + 1

        time.sleep(0.1)

def examiner_process(examiner, student_queue):
    global start_time
    phi = (1 + math.sqrt(5)) / 2
    lunch_taken = False

    while True:
        try:
            # Проверка на обеденный перерыв
            current_time = time.time() - start_time
            if current_time >= 30 and not lunch_taken:
                with examiner_lock:
                    if examiner.current_student is None:
                        lunch_duration = random.uniform(12, 18)
                        time.sleep(lunch_duration)
                        examiner.work_time += lunch_duration
                        lunch_taken = True
                        continue

            # Начало приема студента
            student = student_queue.get_nowait()
            
            # Устанавливаем текущего студента
            with examiner_lock:
                examiner.current_student = student
                examiner.total += 1

            # Имитация времени экзамена
            exam_duration = random.uniform(len(examiner.name)-1, len(examiner.name)+1)
            time.sleep(exam_duration)

            # Процесс экзамена
            result = random.choices([True, False], weights=[0.6, 0.4])[0]
            
            # Обновляем статус студента
            with student_lock:
                student.status = "Сдал" if result else "Провалил"
                student.exam_time = time.time() - start_time

            # Сбрасываем текущего студента
            with examiner_lock:
                examiner.current_student = None
                if not result:
                    examiner.failed += 1

            # Обновляем время работы
            examiner.work_time += exam_duration

        except queue.Empty:
            break

def main():
    read_files()
    student_queue = queue.Queue()
    
    # Заполняем очередь студентов
    for s in students:
        student_queue.put(s)
    
    # Запускаем экзаменаторов
    threads = []
    for e in examiners:
        t = threading.Thread(target=examiner_process, args=(e, student_queue))
        t.start()
        threads.append(t)
    
    # Запускаем обновление интерфейса
    display_thread = threading.Thread(target=update_display)
    display_thread.daemon = True
    display_thread.start()
    
    # Ожидаем завершения
    for t in threads:
        t.join()
    
    # Финальный вывод
    with print_lock:
        print("\033[J")  # Очистка экрана
        
        # Выводим итоговые таблицы
        sorted_students = sorted(students, key=lambda x: x.status != "Сдал")
        print(draw_table(["Студент", "Статус"], [[s.name, s.status] for s in sorted_students]))
        
        examiner_data = [[e.name, str(e.total), str(e.failed), f"{e.work_time:.2f}"] for e in examiners]
        print("\n" + draw_table(["Экзаменатор", "Принято", "Завалено", "Время"], examiner_data))

if __name__ == "__main__":
    main()