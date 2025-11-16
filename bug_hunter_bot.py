#!/usr/bin/env python3
"""
Bug Hunter Bot - Автоматическое прохождение игры "КОД-ХАНТИНГ"
Использует Playwright для автоматизации решения багов
"""

import asyncio
import json
from playwright.async_api import async_playwright, Page
from datetime import datetime


# Словарь решений для Python багов
PYTHON_FIXES = {
    "Функция возвращает None вместо суммы двух чисел": """def add(a, b):
    result = a + b
    return result

print(add(2, 3))""",

    "List comprehension возвращает None вместо списка чисел": """numbers = [1, 2, 3, 4, 5]
even = [n for n in numbers if n % 2 == 0]
print(even)""",

    "Цикл выполняется бесконечно - программа зависает!": """count = 0
while count < 5:
    print(count)
    count += 1

print('Done!')""",

    "Асинхронная функция не ждет результата (несколько багов)": """import asyncio

async def get_data():
    await asyncio.sleep(1)
    data = {'result': 'success'}
    return data

asyncio.run(get_data())""",

    "Словарь изменяется напрямую вместо создания копии (3+ бага)": """state = {'count': 0, 'users': []}

def update_count(new_count):
    return {**state, 'count': new_count}

def add_user(user):
    return {
        **state,
        'users': [*state['users'], user]
    }

new_state = add_user({'id': 1})"""
}


class BugHunterBot:
    def __init__(self, url: str, language: str = "python"):
        self.url = url
        self.language = language
        self.rounds_completed = 0
        self.drink_unlocked = False

    async def run(self):
        """Основной метод запуска бота"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                print(f"🤖 Bug Hunter Bot запущен")
                print(f"🌐 Открываем {self.url}")

                await page.goto(self.url)
                await page.wait_for_load_state("networkidle")

                # Начинаем игру
                await self.start_game(page)

                # Играем минимум 3 раунда
                min_rounds = 3
                while self.rounds_completed < min_rounds:
                    success = await self.play_round(page)
                    if not success:
                        print(f"❌ Ошибка в раунде {self.rounds_completed + 1}")
                        break

                    # Ждем загрузки следующего раунда
                    await asyncio.sleep(2.5)

                # Проверяем результат
                await self.check_final_screen(page)

                # Делаем финальный скриншот
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page.screenshot(path=f"bug_hunter_result_{timestamp}.png")
                print(f"📸 Скриншот сохранен: bug_hunter_result_{timestamp}.png")

                # Держим браузер открытым для просмотра
                print("\n✅ Игра завершена! Проверьте результат в браузере.")
                await asyncio.sleep(5)  # Вместо input() для background режима

            except Exception as e:
                print(f"💥 Ошибка: {e}")
                await page.screenshot(path=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                raise
            finally:
                await browser.close()

    async def start_game(self, page: Page):
        """Начинает игру - выбирает язык и кликает Start"""
        print(f"\n🎮 Начинаем игру")

        # Выбираем язык Python
        print(f"🐍 Выбираем язык: {self.language}")
        await page.select_option("#languageSelector", value=self.language)

        # Кликаем "Начать игру"
        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)

        print(f"✅ Игра началась!")

    async def play_round(self, page: Page) -> bool:
        """Проходит один раунд игры"""
        try:
            # Читаем описание бага
            bug_description_elem = await page.query_selector("#bugDescriptionText")
            if not bug_description_elem:
                print("❌ Не найден элемент с описанием бага")
                return False

            bug_description = await bug_description_elem.inner_text()
            # Извлекаем только заголовок (до "Подсказка:")
            bug_title = bug_description.split("💡")[0].strip()

            print(f"\n🐛 Раунд {self.rounds_completed + 1}: {bug_title}")

            # Находим соответствующее решение
            fixed_code = None
            for key, value in PYTHON_FIXES.items():
                if key in bug_title or bug_title in key:
                    fixed_code = value
                    break

            if not fixed_code:
                print(f"⚠️  Решение не найдено для бага: {bug_title}")
                print(f"📝 Полное описание: {bug_description}")
                return False

            print(f"✅ Найдено решение!")

            # Устанавливаем исправленный код через Monaco API
            # Экранируем бэктики и специальные символы
            escaped_code = fixed_code.replace('`', '\\`').replace('${', '\\${')

            await page.evaluate(f"""
                monaco.editor.getModels()[0].setValue(`{escaped_code}`);
            """)

            print(f"📝 Код установлен в редактор")

            # Ждем немного и вызываем валидацию вручную
            await page.wait_for_timeout(500)

            # Вызываем checkCode() для валидации
            await page.evaluate("checkCode()")

            # Ждем появления feedback и проверяем успех
            await page.wait_for_timeout(500)
            feedback = await page.text_content("#feedback")

            # Bug Hunting показывает сообщения при успехе
            # "🏆 МАСТЕР ДЕБАГА!", "🔍 Баг найден!", "✅ Исправлено!"
            success_keywords = ["МАСТЕР ДЕБАГА", "Баг найден", "Исправлено"]
            if feedback and any(keyword in feedback for keyword in success_keywords):
                self.rounds_completed += 1
                print(f"🎉 Раунд {self.rounds_completed} пройден! {feedback}")
                return True
            else:
                print(f"❌ Валидация не прошла. Feedback: {feedback}")
                return False

        except Exception as e:
            print(f"💥 Ошибка в раунде: {e}")
            await page.screenshot(path=f"round_{self.rounds_completed + 1}_error.png")
            return False

    async def check_final_screen(self, page: Page):
        """Проверяет финальный экран и статус напитка"""
        # Ждем появления финального экрана (может появиться автоматически по таймеру)
        try:
            await page.wait_for_selector("#finalScreen.show", timeout=15000)
        except:
            print("⏱️  Таймер еще не истек, ждем...")
            # Если финальный экран не появился, кликаем "Завершить"
            try:
                await page.click('button:has-text("Завершить")')
                await page.wait_for_timeout(1000)
            except:
                pass

        # Читаем результаты
        try:
            rounds_text = await page.text_content("#finalRoundsCompleted")
            time_text = await page.text_content("#finalTimeSpent")

            print(f"\n" + "="*50)
            print(f"📊 РЕЗУЛЬТАТЫ:")
            print(f"  Раундов завершено: {rounds_text}")
            print(f"  Затрачено времени: {time_text}")

            # Проверяем статус напитка
            drink_unlocked = await page.is_visible("#drinkUnlocked")
            drink_locked = await page.is_visible("#drinkLocked")

            if drink_unlocked:
                print(f"  🍺 Напиток: РАЗБЛОКИРОВАН! ✅")
                self.drink_unlocked = True
            elif drink_locked:
                print(f"  🍺 Напиток: Заблокирован ❌")
                reason_elem = await page.query_selector("#drinkLockedReason")
                if reason_elem:
                    reason = await reason_elem.inner_text()
                    print(f"  💬 Причина: {reason}")

            print("="*50)

        except Exception as e:
            print(f"⚠️  Не удалось прочитать финальный экран: {e}")


async def main():
    """Точка входа"""
    url = "https://mws-code-game.website.yandexcloud.net/bug-hunter.html"
    bot = BugHunterBot(url, language="python")
    await bot.run()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          Bug Hunter Bot - Автоматизация игры               ║
║                     КОД-ХАНТИНГ 🐛                        ║
╚═══════════════════════════════════════════════════════════╝
""")
    asyncio.run(main())
