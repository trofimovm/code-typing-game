#!/usr/bin/env python3
"""
Правильно вставляет мобильные стили в HTML файлы
"""

import re

files = ['bug-hunter.html', 'cloud-architect.html', 'speed-typing.html']

# Читаем мобильные стили
with open('mobile_styles.css', 'r', encoding='utf-8') as f:
    mobile_styles = f.read()

for filename in files:
    print(f"Обрабатываю {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Находим закрывающий тег </style>
    # Вставляем мобильные стили ПЕРЕД ним с отступом
    indented_styles = '\n'.join('        ' + line if line.strip() else ''
                                 for line in mobile_styles.split('\n'))

    # Заменяем </style> на стили + </style>
    new_content = content.replace(
        '    </style>',
        f'\n{indented_styles}\n    </style>',
        1  # только первое вхождение
    )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✅ Стили вставлены в {filename}")

print("✅ Все файлы обработаны!")
