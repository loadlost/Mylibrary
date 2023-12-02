# module_b.py
xpath_values = {
    'epub': {
        'container': 'n:rootfiles/n:rootfile/@full-path',
        'title': '/pkg:package/pkg:metadata/dc:title',
        'creator': '/pkg:package/pkg:metadata/dc:creator'
    },
    'fb2': {
        'title': '//fb:title-info/fb:book-title',
        'author': '//fb:title-info/fb:author',
        'first_name': 'fb:first-name',
        'last_name': 'fb:last-name'
    }
}

namespace = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'
}

initial_document_info = '''<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
    <description>
        <title-info>
            <genre></genre>
            <author><first-name></first-name><last-name></last-name></author>
            <book-title>MyLibrary</book-title>
            <coverpage></coverpage>
            <lang></lang>
            <keywords></keywords>
        </title-info>
        <document-info>
            <author><first-name></first-name><last-name></last-name></author>
            <program-used></program-used>
            <date></date>
            <id></id>
            <version></version>
        </document-info>
        <publish-info>
            <publisher></publisher>
            <year></year>
            <isbn></isbn>
        </publish-info>
    </description>
    <body>
        <section>

        </section>
    </body>
</FictionBook>
'''

# module_b.py
xpath_values = {
    'epub': {
        'container': 'n:rootfiles/n:rootfile/@full-path',
        'title': '/pkg:package/pkg:metadata/dc:title',
        'creator': '/pkg:package/pkg:metadata/dc:creator'
    },
    'fb2': {
        'title': '//fb:title-info/fb:book-title',
        'author': '//fb:title-info/fb:author',
        'first_name': 'fb:first-name',
        'last_name': 'fb:last-name'
    }
}

namespace = {
    'n': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0'
}

initial_document_info = '''<?xml version="1.0" encoding="UTF-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
    <description>
        <title-info>
            <genre></genre>
            <author><first-name></first-name><last-name></last-name></author>
            <book-title>MyLibrary</book-title>
            <coverpage></coverpage>
            <lang></lang>
            <keywords></keywords>
        </title-info>
        <document-info>
            <author><first-name></first-name><last-name></last-name></author>
            <program-used></program-used>
            <date></date>
            <id></id>
            <version></version>
        </document-info>
        <publish-info>
            <publisher></publisher>
            <year></year>
            <isbn></isbn>
        </publish-info>
    </description>
    <body>
        <section>

        </section>
    </body>
</FictionBook>
'''

# Добавляем переменные ns и ns_map
ns_output = {'fb': 'http://www.gribuser.ru/xml/fictionbook/2.0', 'xlink': 'http://www.w3.org/1999/xlink'}
