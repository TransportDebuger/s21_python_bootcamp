import asyncio
import os
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError

def get_save_directory():
    while True:
        directory = input("Введите путь для сохранения изображений: ").strip()
        if not directory:
            print("Путь не может быть пустым.")
            continue
            
        if os.path.isfile(directory):
            print("Ошибка: Указанный путь ведёт к файлу, а не к директории.")
            continue
            
        try:
            # Попытка создания директории (если не существует)
            os.makedirs(directory, exist_ok=True)
            
            # Проверка прав доступа
            if os.access(directory, os.W_OK):
                return directory
            print("Ошибка: Нет прав на запись в указанную директорию.")
            
        except PermissionError:
            print("Ошибка: Недостаточно прав для создания директории.")
        except OSError as e:
            print(f"Ошибка создания директории: {e}")

async def async_input(prompt: str) -> str:
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

async def download_image(url, directory, results):
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: urllib.request.urlopen(url)
        )
        
        if response.status == 200:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or "image.jpg"
            save_path = os.path.join(directory, filename)
            
            content = response.read()
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: open(save_path, 'wb').write(content)
            )
            
            results.append((url, "Успех"))
        else:
            results.append((url, "Ошибка"))
    except (URLError, HTTPError, OSError, ValueError) as e:
        results.append((url, "Ошибка"))

async def main():
    save_dir = get_save_directory()
    results = []
    tasks = []
    
    # Обработка ввода ссылок
    while True:
        url = await async_input("Введите ссылку на изображение: ")
        if not url.strip():
            break
        task = asyncio.create_task(download_image(url, save_dir, results))
        tasks.append(task)
    
    # Ожидание завершения всех задач
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    
    # Вывод результатов
    print("\nСводка об успешных и неуспешных загрузках\n")
    max_url_len = max(len(url) for url, _ in results) if results else 20
    max_status_len = max(len(status) for _, status in results) if results else 6
    
    separator = f"+{'-' * (max_url_len + 2)}+{'-' * (max_status_len + 2)}+"
    print(separator)
    print(f"| {'Ссылка'.ljust(max_url_len)} | {'Статус'.ljust(max_status_len)} |")
    print(separator)
    
    for url, status in results:
        print(f"| {url.ljust(max_url_len)} | {status.ljust(max_status_len)} |")
    
    print(separator)

if __name__ == "__main__":
    asyncio.run(main())