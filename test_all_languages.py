#!/usr/bin/env python3
"""
Автоматическое тестирование Bug Hunter для всех языков
Проходит минимум 10 раундов на каждом языке, проверяя что игра работает
"""

import asyncio
import json
from playwright.async_api import async_playwright, Page
from datetime import datetime


# Загружаем реальные решения из извлеченного JSON
with open("language_fixes.json", "r", encoding="utf-8") as f:
    LANGUAGE_FIXES = json.load(f)


class BugHunterTester:
    def __init__(self, url: str):
        self.url = url
        self.results = {}

    async def test_language(self, page: Page, language: str, language_value: str):
        """Тестирует один язык программирования"""
        print(f"\n{'='*60}")
        print(f"🧪 Тестирование языка: {language.upper()}")
        print(f"{'='*60}")

        # Перезагружаем страницу для нового теста
        await page.goto(self.url)
        await page.wait_for_load_state("networkidle")

        # Выбираем язык
        await page.select_option("#languageSelector", value=language_value)
        print(f"✅ Выбран язык: {language}")

        # Начинаем игру
        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)
        print(f"✅ Игра началась")

        fixes = LANGUAGE_FIXES.get(language, LANGUAGE_FIXES["javascript"])
        rounds_completed = 0
        max_rounds = 10
        errors = []

        while rounds_completed < max_rounds:
            try:
                # Читаем описание бага
                bug_elem = await page.query_selector("#bugDescriptionText")
                if not bug_elem:
                    errors.append(f"Round {rounds_completed + 1}: Bug description not found")
                    break

                bug_text = await bug_elem.inner_text()
                bug_title = bug_text.split("💡")[0].strip() if "💡" in bug_text else bug_text

                print(f"\n🐛 Раунд {rounds_completed + 1}: {bug_title[:60]}...")

                # Используем циклический индекс для получения решения
                fix_index = rounds_completed % len(fixes)
                fixed_code = fixes[fix_index]

                # Устанавливаем исправленный код
                escaped_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')

                await page.evaluate(f"""
                    monaco.editor.getModels()[0].setValue(`{escaped_code}`);
                """)

                # setValue автоматически триггерит checkCode() через onDidChangeModelContent
                # Ждем короткую паузу для выполнения checkCode() и roundComplete()
                await page.wait_for_timeout(500)

                # Читаем feedback ДО того как nextRound() очистит его (roundComplete делает setTimeout 2000ms)
                feedback = await page.text_content("#feedback")

                success_keywords = ["МАСТЕР ДЕБАГА", "Баг найден", "Исправлено", "ОГОНЬ", "Быстро"]
                if feedback and any(keyword in feedback for keyword in success_keywords):
                    rounds_completed += 1
                    print(f"✅ Раунд {rounds_completed} пройден! {feedback}")

                    # Ждем автоматического перехода к следующему раунду
                    await page.wait_for_timeout(2500)
                else:
                    print(f"❌ Валидация не прошла. Feedback: {feedback}")
                    errors.append(f"Round {rounds_completed + 1}: Validation failed - {feedback}")
                    break

            except Exception as e:
                error_msg = f"Round {rounds_completed + 1}: {str(e)}"
                print(f"💥 Ошибка: {error_msg}")
                errors.append(error_msg)

                # Делаем скриншот для отладки
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page.screenshot(path=f"error_{language}_{timestamp}.png")
                break

        # Сохраняем результаты
        self.results[language] = {
            "rounds_completed": rounds_completed,
            "errors": errors,
            "success": rounds_completed >= max_rounds and len(errors) == 0
        }

        print(f"\n📊 Результаты для {language.upper()}:")
        print(f"  Раундов пройдено: {rounds_completed}/{max_rounds}")
        print(f"  Статус: {'✅ Успех' if self.results[language]['success'] else '❌ Есть проблемы'}")
        if errors:
            print(f"  Ошибки: {len(errors)}")
            for error in errors:
                print(f"    - {error}")

    async def run_all_tests(self):
        """Запускает тесты для всех языков"""
        languages = [
            ("javascript", "javascript"),
            ("python", "python"),
            ("cpp", "cpp"),
            ("csharp", "csharp"),
            ("java", "java"),
            ("golang", "golang"),
        ]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                for lang_name, lang_value in languages:
                    await self.test_language(page, lang_name, lang_value)
                    await page.wait_for_timeout(2000)

                # Финальный отчет
                print(f"\n{'='*60}")
                print(f"📊 ФИНАЛЬНЫЙ ОТЧЕТ")
                print(f"{'='*60}")

                total_passed = sum(1 for r in self.results.values() if r['success'])
                total_langs = len(self.results)

                for lang, result in self.results.items():
                    status = "✅" if result['success'] else "❌"
                    print(f"{status} {lang.upper()}: {result['rounds_completed']}/10 раундов")
                    if result['errors']:
                        for error in result['errors']:
                            print(f"      {error}")

                print(f"\n{'='*60}")
                print(f"Языков протестировано: {total_langs}")
                print(f"Успешно пройдено: {total_passed}")
                print(f"С ошибками: {total_langs - total_passed}")
                print(f"{'='*60}")

                # Сохраняем отчет в JSON
                with open("test_results.json", "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                print(f"\n📄 Отчет сохранен в test_results.json")

            finally:
                await browser.close()


async def main():
    url = "https://mws-code-game.website.yandexcloud.net/bug-hunter.html"
    tester = BugHunterTester(url)
    await tester.run_all_tests()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║    Bug Hunter - Автоматическое тестирование всех языков   ║
╚═══════════════════════════════════════════════════════════╝
""")
    asyncio.run(main())
