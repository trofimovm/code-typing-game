#!/usr/bin/env python3
"""
Автоматическое тестирование Bug Hunter с новыми 10 багами
Загружает решения из bugs-data.json
"""
import asyncio
import json
from playwright.async_api import async_playwright, Page
from datetime import datetime


# Загружаем решения из bugs-data.json
with open("bugs-data.json", "r", encoding="utf-8") as f:
    BUGS_DATA = json.load(f)


class BugHunterTester:
    def __init__(self, url: str):
        self.url = url
        self.results = {}

    async def test_language(self, page: Page, language: str):
        """Тестирует один язык"""
        print(f"\n{'='*60}")
        print(f"🧪 Тестирование: {language.upper()}")
        print(f"{'='*60}")

        await page.goto(self.url)
        await page.wait_for_load_state("networkidle")
        
        # Ждем загрузки bugs-data.json
        await page.wait_for_timeout(2000)

        await page.select_option("#languageSelector", value=language)
        print(f"✅ Выбран язык: {language}")

        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)
        print(f"✅ Игра началась")

        bugs = BUGS_DATA.get(language, [])
        rounds_completed = 0
        max_rounds = 10
        errors = []

        for round_num in range(max_rounds):
            try:
                bug_elem = await page.query_selector("#bugDescriptionText")
                if not bug_elem:
                    errors.append(f"Round {round_num + 1}: Bug description not found")
                    break

                bug_text = await bug_elem.inner_text()
                bug_title = bug_text.split("💡")[0].strip() if "💡" in bug_text else bug_text

                print(f"\n🐛 Раунд {round_num + 1}: {bug_title[:60]}...")

                # Берем правильное решение
                bug_index = round_num % len(bugs)
                fixed_code = bugs[bug_index]["fixedCode"]

                # Устанавливаем код
                escaped_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')
                
                await page.evaluate(f"""
                    monaco.editor.getModels()[0].setValue(`{escaped_code}`);
                """)

                # setValue автоматически триггерит checkCode()
                await page.wait_for_timeout(500)

                # Читаем feedback ДО nextRound()
                feedback = await page.text_content("#feedback")

                success_keywords = ["МАСТЕР ДЕБАГА", "Баг найден", "Исправлено", "ОГОНЬ", "Быстро"]
                if feedback and any(keyword in feedback for keyword in success_keywords):
                    rounds_completed += 1
                    print(f"✅ Раунд {rounds_completed} пройден! {feedback}")
                    await page.wait_for_timeout(2500)
                else:
                    print(f"❌ Валидация не прошла. Feedback: {feedback}")
                    errors.append(f"Round {round_num + 1}: Validation failed - {feedback}")
                    break

            except Exception as e:
                error_msg = f"Round {round_num + 1}: {str(e)}"
                print(f"💥 Ошибка: {error_msg}")
                errors.append(error_msg)
                break

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
        languages = ["javascript", "python", "cpp", "csharp", "java"]

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                for lang in languages:
                    await self.test_language(page, lang)
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

                with open("test_results_new.json", "w", encoding="utf-8") as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                print(f"\n📄 Отчет сохранен в test_results_new.json")

            finally:
                await browser.close()


async def main():
    url = "https://mws-code-game.website.yandexcloud.net/bug-hunter.html"
    tester = BugHunterTester(url)
    await tester.run_all_tests()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║       Bug Hunter - Тестирование новых 10 багов            ║
╚═══════════════════════════════════════════════════════════╝
""")
    asyncio.run(main())
