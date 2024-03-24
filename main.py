# main.py обрабатывает EPUB и FB2 файлы, организуя их по авторам в папке 'books'.

import zipfile
from lxml import etree
import os
import re
import shutil
from fb2_output import create_fb2_file
from config import xpath_values, namespace, ns_output


def normalize_filename(filename):
    # Функция нормализует имя файла, удаляя лишние пробелы и символы.
    # Принимает строку `filename` - текущее имя файла.
    # Возвращает строку - нормализованное имя файла.

    filename = filename.lstrip()  # Удаление начальных пробелов
    filename = ' '.join(filename.split())  # Замена множественных пробелов на один
    table = str.maketrans("", "", r"?!@#$%^&*_+|+/\:;[]{}<>=")  # Таблица для удаления определенных символов
    return filename.translate(table)  # Возврат нормализованного имени файла


def read_metadata_from_file(file, format_type):
    # Читает метаданные из файлов EPUB и FB2.
    # Принимает `file` - путь к файлу, `format_type` - расширение (EPUB или FB2).
    # Возвращает объект ElementTree - дерево элементов XML с метаданными.

    tree = None
    xpath = xpath_values[format_type]  # Получение соответствующих значений XPath из config.py
    ns = namespace

    try:
        if file.endswith('.epub'):
            archive = zipfile.ZipFile(file)  # Открывает EPUB-архив
            txt = archive.read('META-INF/container.xml')  # Читает файл container.xml
            container_tree = etree.fromstring(txt)  # Создает дерево элементов из container.xml
            container_file_name = container_tree.xpath(xpath['container'], namespaces=ns)[
                0]  # Находит имя основного файла
            container_file = archive.read(container_file_name)  # Читает содержимое основного файла
            tree = etree.fromstring(container_file)  # Создает дерево элементов из основного файла
            archive.close()  # Закрывает архив
        elif file.endswith('.fb2'):
            tree = etree.parse(file)  # Читает FB2-файл
    except Exception as e:
        print(f"Error reading metadata from {file}: {e}")  # Выводит сообщение об ошибке, если что-то идет не так

    return tree  # Возвращает дерево элементов XML с метаданными


def set_new_filename(title, authors, extension):
    # Формирует новое нормализованное имя файла на основе заголовка, авторов и расширения.
    # Принимает `title` - заголовок книги, список `authors` - имена авторов, `extension` - расширение файла.
    # Возвращает строку - нормализованное имя файла.

    new_name = f'«{title}», {", ".join(authors)}.{extension}'  # Составление нового имени файла
    return normalize_filename(new_name)  # Возврат нормализованного имени файла


def process_common(file, author_dict, extension, title, author_names):
    # Общая функция для обработки файлов, формирует новое имя, перемещает файл и обновляет словарь авторов.
    # Принимает `file` - путь к файлу, словарь `author_dict` - словарь авторов,
    # `extension` - расширение файла, `title` - заголовок книги, список `author_names` - имена авторов.

    new_name = set_new_filename(title, author_names, extension)  # Формирование нового нормализованного имени файла
    os.rename(file, f'books/{new_name}')  # Переименование файла с учетом нового имени и перемещение в папку 'books'

    key = ", ".join(author_names)  # Формирование ключа для словаря авторов
    key = normalize_filename(key)  # Нормализация ключа
    if key not in author_dict:
        author_dict[key] = set()
    author_dict[key].add(new_name)  # Добавление нового имени в множество автора


def process_epub(file, author_dict):
    # Обрабатывает файл формата EPUB, извлекает метаданные и вызывает общую функцию для обработки.
    # Принимает `file` - путь к файлу и словарь `author_dict` - словарь авторов.

    format_type = 'epub'
    xpath = xpath_values[format_type]  # Получение соответствующих значений XPath из конфигурации
    ns = namespace
    tree = read_metadata_from_file(file, format_type)  # Получение дерева элементов с метаданными из файла

    if tree is not None:
        title = tree.xpath(xpath['title'], namespaces=ns)[0]  # Извлечение заголовка книги
        creators = tree.xpath(xpath['creator'], namespaces=ns)  # Извлечение списка авторов
        author_names = [creator.text for creator in creators]  # Формирование списка имен авторов
        process_common(file, author_dict, 'epub', title.text, author_names)  # Вызов общей функции для обработки
    # else:
    #     print(f"Error processing EPUB file: {file}")


def process_fb2(file, author_dict):
    # Обрабатывает файл формата FB2, извлекает метаданные и вызывает общую функцию для обработки.
    # Принимает строку `file` - путь к файлу и словарь `author_dict` - словарь авторов.

    format_type = 'fb2'
    xpath = xpath_values[format_type]  # Получение соответствующих значений XPath из конфигурации
    ns = namespace
    tree = read_metadata_from_file(file, format_type)  # Получение дерева элементов с метаданными из файла

    if tree is not None:
        title = tree.xpath(xpath['title'], namespaces=ns)  # Извлечение заголовка книги
        title = title[0].text.strip() if title and title[0].text else 'Unknown Title'  # Проверка и получение заголовка
        author_elements = tree.xpath(xpath['author'], namespaces=ns)  # Извлечение элементов имени авторов
        author_names = [
            f"{author.xpath(xpath['first_name'], namespaces=ns)[0].text} "
            f"{author.xpath(xpath['last_name'], namespaces=ns)[0].text}"
            if author.xpath(xpath['first_name'], namespaces=ns) and author.xpath(xpath['last_name'], namespaces=ns)
            else author.xpath(xpath['first_name'], namespaces=ns)[0].text
            if author.xpath(xpath['first_name'], namespaces=ns)
            else 'Unknown'
            for author in author_elements]  # Формирование списка имен авторов
        process_common(file, author_dict, 'fb2', title, author_names)  # Вызов общей функции для обработки
    else:
        pass
        # print(f"Error processing FB2 file: {file}")


def compare_and_merge_keys(author_dict):
    # Сравнивает и объединяет ключи словаря авторов на основе фамилий.
    # Принимает словарь 'author_dict' - словарь авторов.
    # Возвращает словарь 'merged_dict' - объединенный словарь авторов.

    merged_dict = {}
    while author_dict:
        key1, books1 = author_dict.popitem()  # Извлекает ключ и соответствующее множество книг
        author_last_names = set(author.split()[-1] for author in key1.split(', '))  # Извлекает фамилии из ключа
        matching_keys = [key2 for key2 in author_dict.keys() if set(author.split()[-1] for author in key2.split(', '))
                         == author_last_names]  # Ищет ключи с совпадающими фамилиями
        if matching_keys:
            merged_books = books1.union(*[author_dict[key] for key in matching_keys])  # Объединяет множества книг
            for key in matching_keys:
                del author_dict[key]  # Удаляет совпадающие ключи из исходного словаря
            merged_dict[key1] = merged_books  # Добавляет объединенное множество в новый словарь
        else:
            merged_dict[key1] = books1  # Если совпадений нет, добавляет множество в новый словарь

    return merged_dict  # Возвращает объединенный словарь авторов


def organize_books_by_author(merged_dict, base_folder='books'):
    # Организует книги по авторам в структуру папок, создавая папки для каждого автора и перемещая файлы.
    # Принимает словарь `merged_dict` - объединенный словарь авторов и `base_folder` - базовая папка.

    os.makedirs(base_folder, exist_ok=True)  # Создает базовую папку, если её нет
    for authors, books in merged_dict.items():
        author_folder = os.path.join(base_folder, authors)  # Формирует путь к папке автора
        os.makedirs(author_folder, exist_ok=True)  # Создает папку автора, если её нет
        for book in books:
            source_path = find_book_path('books', book)  # Находит путь к исходному файлу
            destination_path = os.path.join(author_folder, book)  # Формирует путь к целевому файлу
            if source_path and source_path != destination_path:
                try:
                    shutil.move(source_path, destination_path)  # Перемещает файл в папку автора
                # print(f"Moved '{book}' to '{author_folder}'")
                except Exception as e:
                    print(f"Error moving '{book}': {e}")  # Выводит сообщение об ошибке, если что-то идет не так


def find_book_path(base_folder, book):
    # Находит полный путь к файлу `book` в структуре папок, начиная с базовой папки.
    # Принимает строку `base_folder` - базовая папка и строку `book` - имя файла.
    # Возвращает строку - полный путь к файлу или None, если файл не найден.

    for root, dirs, files in os.walk(base_folder):
        if book in files:
            return os.path.join(root, book)  # Возвращает полный путь к файлу
    return None  # Возвращает None, если файл не найден


def create_author_dict(folder_author):
    # Создает словарь авторов на основе файлов в папках авторов.
    # Принимает `folder_author` - путь к папке авторов.
    # Возвращает словарь - словарь авторов, где ключи - имена авторов, значения - множества файлов.

    author_dict = {}
    if not os.path.exists(folder_author):  # Проверка наличия папки авторов
        return author_dict

    folders = [f for f in os.listdir(folder_author) if
               os.path.isdir(os.path.join(folder_author, f))]  # Получение списка папок
    for folder in folders:
        author_folder_path = os.path.join(folder_author, folder)  # Формирование пути к папке автора
        if os.path.isdir(author_folder_path):
            files = [f for f in os.listdir(author_folder_path) if
                     os.path.isfile(os.path.join(author_folder_path, f))]  # Получение списка файлов
            author_dict[folder] = set(files)  # Добавление в словарь: ключ - имя автора, значение - множество файлов

    return author_dict  # Возвращает словарь авторов


def remove_empty_folders(base_folder='books'):
    # Удаляет пустые папки в структуре папок начиная с базовой папки.
    # Принимает `base_folder`.

    for root, folders, files in os.walk(base_folder, topdown=False):
        for folder in folders:
            author_folder = os.path.join(root, folder)  # Формирует путь к папке автора
            if not os.listdir(author_folder):  # Проверяет, является ли папка пустой
                try:
                    os.rmdir(author_folder)  # Удаляет пустую папку
                #     print(f"Removed empty folder: {author_folder}")
                except Exception as e:
                    # Выводит сообщение об ошибке, если что-то идет не так
                    print(f"Error removing empty folder {author_folder}: {e}")


def process_books_in_folder(folder):
    # Обрабатывает книги в указанной папке, создавая и организуя структуру файлов и папок.
    # Принимает `folder` - путь к папке с книгами.

    author_dict = create_author_dict(folder)  # Создает словарь авторов на основе файлов в папке
    for file in os.listdir(folder):
        try:
            if file == 'output.fb2':
                continue
            if re.fullmatch(r'.*\.epub', file):
                process_epub(os.path.join(folder, file), author_dict)  # Обрабатывает EPUB
            elif re.fullmatch(r'.*\.fb2', file):
                process_fb2(os.path.join(folder, file), author_dict)  # Обрабатывает FB2
        except Exception as e:
            print(f"Error processing {file}: {e}")

    merged_author_dict = compare_and_merge_keys(author_dict)  # Сравнивает и объединяет авторов
    organize_books_by_author(merged_author_dict)  # Организует книги по авторам
    create_fb2_file(merged_author_dict, ns_output)  # Создает файл формата FB2
    remove_empty_folders()  # Удаляет пустые папки

    # print("----- Merged Author Dictionary -----")
    # for authors, books in merged_author_dict.items():
    #     print(authors)
    #     for book in books:
    #         print(f"  - {book}")
    # print(merged_author_dict)


if __name__ == "__main__":
    folder_path = os.path.join(os.getcwd(), 'Books')  # Формирует путь к папке с книгами
    process_books_in_folder(folder_path)  # Вызывает функцию обработки книг в указанной папке
