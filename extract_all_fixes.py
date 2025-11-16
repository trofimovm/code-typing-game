#!/usr/bin/env python3
"""
Извлекает все fixedCode из bug-hunter.html для всех языков
"""

import re
import json

def extract_language_fixes(content, language_key):
    """Извлекает исправленный код для одного языка"""

    # Ищем секцию языка
    pattern = rf"'{language_key}':\s*\[(.*?)\],\s*'[a-z]+':"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"Не найдена секция для {language_key}")
        return []

    lang_section = match.group(1)

    # Извлекаем все fixedCode
    fixed_codes = re.findall(r'fixedCode:\s*`(.*?)`', lang_section, re.DOTALL)

    return fixed_codes

def main():
    # Читаем файл
    with open("/Users/mikhailtrofimov/code/code-typing-game/bug-hunter.html", "r", encoding="utf-8") as f:
        content = f.read()

    languages = ["javascript", "python", "cpp", "csharp", "java", "golang"]
    all_fixes = {}

    for lang in languages:
        fixes = extract_language_fixes(content, lang)
        all_fixes[lang] = fixes
        print(f"{lang.upper()}: {len(fixes)} багов")

    # Сохраняем в JSON
    with open("language_fixes.json", "w", encoding="utf-8") as f:
        json.dump(all_fixes, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Все исправления сохранены в language_fixes.json")

if __name__ == "__main__":
    main()
