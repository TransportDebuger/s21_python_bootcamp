import threading
import queue
import time
import random
import math
from sys import exit
from collections import defaultdict

students = []
examiners = []
questions = []
student_lock = threading.Lock()
examiner_lock = threading.Lock()
start_time = time.time()
print_lock = threading.Lock()

class Question:
    def __init__(self, text):
        self.text = text
        self.words = text.split()

    def generate_student_answer(self, gender):
        """Генерация ответа студента с учетом гендера и золотого сечения"""
        phi = (1 + math.sqrt(5)) / 2
        n = len(self.words)
        probabilities = []
        
        # Генерация вероятностей
        remaining = 1.0
        if gender == 'М':
            for _ in range(n):
                p = remaining / phi
                probabilities.append(p)
                remaining -= p
        else:  # Для 'Ж'
            for _ in reversed(range(n)):
                p = remaining / phi
                probabilities.insert(0, p)
                remaining -= p
        
        # Нормализация
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        return random.choices(self.words, weights=probabilities)[0]

    def generate_examiner_answers(self):
        """Генерация правильных ответов экзаменатором"""
        answers = set()
        available_words = self.words.copy()
        
        while True:
            if not available_words:
                break
            word = random.choice(available_words)
            answers.add(word)
            available_words.remove(word)
            if random.random() > 1/3:  # 2/3 вероятность остановиться
                break
        return answers

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
        self.lunch_taken = False

def read_files():
    try:
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
    
    col_widths = [
        max(len(str(row[i])) for row in data + [headers])
        for i in range(len(headers))
    ]
    
    header = "|".join(f" {h.ljust(w)} " for h, w in zip(headers, col_widths))
    separator = "+".join("-" * (w + 2) for w in col_widths)
    rows = []
    
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
            with student_lock:
                sorted_students = sorted(students, key=lambda x: ["Очередь", "Сдал", "Провалил"].index(x.status))
                student_table = draw_table(["Студент", "Статус"], [[s.name, s.status] for s in sorted_students])
            
            with examiner_lock:
                examiner_data = [[e.name, 
                                e.current_student.name if e.current_student else "-",
                                e.total,
                                e.failed,
                                f"{e.work_time:.2f}"] for e in examiners]
                examiner_table = draw_table(["Экзаменатор", "Текущий студент", "Всего", "Завалено", "Время"], examiner_data)
            
            with student_lock:
                remaining = sum(1 for s in students if s.status == "Очередь")
                output = f"{student_table}\n{examiner_table}\n\nОсталось: {remaining} из {len(students)}\nВремя: {time.time()-start_time:.2f}"
                
            print(f"\033[{prev_lines}F\033[J{output}", end="", flush=True)
            prev_lines = output.count('\n')+1
        time.sleep(0.1)

def examiner_process(examiner, student_queue):
    global start_time

    while True:
        try:
            # Проверка на обеденный перерыв
            current_time = time.time() - start_time
            if current_time >= 30 and not examiner.lunch_taken:
                with examiner_lock:
                    examiner.current_student = None
                    examiner.on_lunch = True
                
                lunch_duration = random.uniform(12, 18)
                time.sleep(lunch_duration)
                examiner.work_time += lunch_duration
                examiner.lunch_taken = True
                examiner.on_lunch = False
            else:
                # Начало приема студента
                student = student_queue.get_nowait()
            
                # Устанавливаем текущего студента
                with examiner_lock:
                    examiner.current_student = student
                    examiner.total += 1

                # Имитация времени экзамена
                exam_duration = random.uniform(len(examiner.name)-1, len(examiner.name)+1)
                time.sleep(exam_duration)

                student.answers = []  # Очищаем предыдущие ответы
                for _ in range(3):  # 3 вопроса
                    q_text = random.choice(questions)
                    question = Question(q_text)
                
                    # Ответ студента
                    student_answer = question.generate_student_answer(student.gender)
                
                    # Ответы экзаменатора
                    correct_answers = question.generate_examiner_answers()
                    is_correct = student_answer in correct_answers
                
                    student.answers.append( (q_text, student_answer, is_correct) )

                # Процесс экзамена
                mood = random.choices(['bad', 'good', 'neutral'], weights=[1/8, 1/4, 5/8])
                if mood == 'bad':
                    result = False
                elif mood == 'good':
                    result = True
                else:
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
        
        # Таблица студентов
        sorted_students = sorted(
            students, 
            key=lambda x: (x.status == "Провалил", x.exam_time or 0)
        )
        student_data = [[s.name, s.status] for s in sorted_students]
        print(draw_table(["Студент", "Статус"], student_data))
        
        # Таблица экзаменаторов
        examiner_data = [
            [e.name, str(e.total), str(e.failed), f"{e.work_time:.2f}"] 
            for e in examiners
        ]
        print("\n" + draw_table(
            ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"],
            examiner_data
        ))
        
        # Дополнительная информация
        total_time = time.time() - start_time
        print(f"\nВремя с момента начала экзамена: {total_time:.2f} сек.")
        
        # Лучшие студенты
        passed = [s for s in students if s.status == "Сдал"]
        if passed:
            min_time = min(s.exam_time for s in passed)
            best_students = [s.name for s in passed if s.exam_time == min_time]
            print(f"Имена лучших студентов: {', '.join(best_students)}")
        else:
            print("Имена лучших студентов: нет")
        
        # Лучшие экзаменаторы
        examiner_stats = []
        for e in examiners:
            if e.total == 0:
                rate = 0.0
            else:
                rate = e.failed / e.total
            examiner_stats.append((e, rate))
        
        if examiner_stats:
            min_rate = min(stats[1] for stats in examiner_stats)
            best_examiners = [e.name for e, r in examiner_stats if r == min_rate]
            print(f"Имена лучших экзаменаторов: {', '.join(best_examiners)}")
        
        # Отчисленные студенты
        failed = [s for s in students if s.status == "Провалил"]
        if failed:
            min_time = min(s.exam_time for s in failed)
            earliest_failed = [s for s in failed if s.exam_time == min_time]
            names = ", ".join(s.name for s in earliest_failed)
            print(f"Имена студентов, которых отчислят: {names}")
        
        # Лучшие вопросы
        question_stats = defaultdict(int)
        for s in students:
            for ans in s.answers:
                if ans[2]:  # Если ответ правильный
                    question_stats[ans[0]] += 1  # Увеличиваем счетчик вопроса

        if question_stats:
            max_correct = max(question_stats.values())
            if max_correct > 0:
                best_questions = [q for q, c in question_stats.items() if c == max_correct]
                print(f"Лучшие вопросы: {', '.join(best_questions)}")
            else:
                print("Лучшие вопросы: нет вопросов с правильными ответами")
        else:
            print("Лучшие вопросы: данные отсутствуют")
        
        # Итог экзамена
        pass_rate = len(passed) / len(students) if students else 0
        print("\nВывод:", "экзамен удался" if pass_rate > 0.85 else "экзамен не удался")

if __name__ == "__main__":
    main()