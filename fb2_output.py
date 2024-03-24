# Модуль для создания FB2 файла из словаря авторов.

import os
from lxml import etree
import xml.dom.minidom
import re
from config import initial_document_info


def create_fb2_file(merged_author_dict, ns):
    # Создает FB2 файл на основе объединенного словаря авторов.
    # Принимает словарь `merged_author_dict` - объединенный словарь авторов и пространство имен `ns`.
    # Возвращает строку - содержание файла формата FB2.

    root = etree.fromstring(initial_document_info.encode('utf-8'))  # Создает корневой элемент с начальной информацией


    for author, books in merged_author_dict.items():
        create_author_block(root, author, books, ns)  # Создает блок данных для каждого автора
    # Удаляет дублирующиеся строки
    updated_content = remove_duplicate_lines_in_section(etree.tostring(root, encoding='utf-8').decode('utf-8'))
    # Проверяет и удаляет несуществующие ссылки
    updated_content = check_and_remove_nonexistent_links(updated_content, ns)
    updated_content = remove_empty_subtitles(updated_content, ns)  # Удаляет пустые подзаголовки
    dom = xml.dom.minidom.parseString(updated_content)  # Создает объект DOM для форматирования
    formatted_content = dom.toprettyxml(indent="  ")  # Форматирует содержание

    return save_to_fb2_file(formatted_content)  # Сохраняет содержание в файл формата FB2


def remove_duplicate_lines_in_section(content):
    # Удаляет дублирующиеся строки в XML структуре.
    # Принимает строку `content` - содержание FB2 файла.
    # Возвращает строку - содержание с удаленными дублирующимися строками.

    lines = content.split('\n')  # Разбивает содержание на строки

    unique_lines = []
    seen_lines = set()

    for line in lines:
        if line not in seen_lines or '<empty-line/>' in line:
            unique_lines.append(line)  # Добавляет строку в новый список, если она уникальна или является пустой строкой
            seen_lines.add(line)  # Добавляет строку в множество просмотренных строк

    return '\n'.join(unique_lines)  # Объединяет уникальные строки в одну строку


def check_and_remove_nonexistent_links(content, ns):
    # Проверяет и удаляет несуществующие ссылки из XML структуры FB2 файла.
    # Принимает строку `content` - содержание FB2 файла. и пространство имен `ns`.
    # Возвращает строку - содержание с удаленными несуществующими ссылками.

    tree = etree.fromstring(content)  # Создает объект ElementTree из XML строки

    for link in tree.xpath('.//fb:a[@xlink:href]', namespaces=ns):
        xlink_href = os.path.join('books', link.get(f"{{{ns['xlink']}}}href"))  # Формирует полный путь к файлу
        is_file_exists = os.path.isfile(xlink_href)  # Проверяет, существует ли файл

        if not is_file_exists:
            parent = link.getparent()
            parent.getparent().remove(parent)  # Удаляет элемент из структуры, если файл не существует
    # Преобразует структуру обратно в строку
    return etree.tostring(tree, encoding='utf-8', xml_declaration=True).decode('utf-8')


def remove_empty_subtitles(content, ns):
    # Удаляет пустые подзаголовки из XML структуры FB2 файла.
    # Принимает строку `content` - содержание FB2 файла и пространство имен `ns`.
    # Возвращает строку - содержание с удаленными пустыми подзаголовками.

    tree = etree.fromstring(content.encode('utf-8'))  # Создает объект ElementTree из XML строки

    for subtitle_element in tree.xpath('.//fb:subtitle', namespaces=ns):
        next_element = subtitle_element.getnext()

        if next_element is not None and next_element.tag.endswith('p'):
            continue
        else:
            parent = subtitle_element.getparent()
            parent.remove(subtitle_element)  # Удаляет элемент из структуры, если следующий элемент не является абзацем
    # Преобразует структуру обратно в строку
    return etree.tostring(tree, encoding='utf-8', xml_declaration=True).decode('utf-8')


def create_author_block(root, author, books, ns):
    # Создает блок данных для каждого автора в XML структуре.
    # Принимает элемент `root`, строку `author` - имя автора, список `books` - книги автора и пространство имен `ns`.

    # Создает элемент подзаголовка
    subtitle_element = etree.SubElement(root.find(".//fb:section", namespaces=ns), 'subtitle')
    subtitle_element.text = author  # Устанавливает текст подзаголовка как имя автора

    for book in books:
        match = re.search(r'«(.*?)»', book)

        if match:
            title = match.group(1)
            # Создает элемент абзаца
            p_element = etree.SubElement(root.find(".//fb:section", namespaces=ns), 'p', name='book')
            # Создает элемент ссылки на книгу

            a_element = etree.SubElement(p_element, 'a', {f"{{{ns['xlink']}}}href": f"{author}/{book}"})


            a_element.text = f'  - {title}'  # Устанавливает текст ссылки

    etree.SubElement(root.find(".//fb:section", namespaces=ns), 'empty-line')  # Добавляет пустую строку


def save_to_fb2_file(content):
    # Сохраняет содержание в файл формата FB2.
    # Принимает строку `content` - XML структура.

    with open('books/output.fb2', 'w', encoding='utf-8') as file:
        file.write(content)  # Записывает содержание в файл формата FB2
