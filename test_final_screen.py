#!/usr/bin/env python3
"""
Тестирование финального экрана Bug Hunter
Проверяет:
1. Видимость финального экрана после завершения игры
2. Отображение количества пройденных раундов
3. Соответствие цветовой схеме игры (фиолетовый для Bug Hunter)
"""
import asyncio
import json
from playwright.async_api import async_playwright, Page

# Загружаем решения из bugs-data.json
with open("bugs-data.json", "r", encoding="utf-8") as f:
    BUGS_DATA = json.load(f)


async def test_final_screen():
    """Тестирует финальный экран после досрочного завершения игры"""
    url = "https://mws-code-game.website.yandexcloud.net/bug-hunter.html"
    language = "javascript"

    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ ФИНАЛЬНОГО ЭКРАНА - BUG HUNTER")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Обработчик для confirm dialog
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        try:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            # Выбираем язык
            await page.select_option("#languageSelector", value=language)
            print(f"✅ Выбран язык: {language}")

            # Начинаем игру
            await page.click('button:has-text("Начать игру")')
            await page.wait_for_timeout(1000)
            print(f"✅ Игра началась")

            bugs = BUGS_DATA.get(language, [])
            rounds_completed = 0

            # Проходим 3 раунда
            for round_num in range(3):
                bug_index = round_num % len(bugs)
                fixed_code = bugs[bug_index]["fixedCode"]

                # Экранируем код
                escaped_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')

                # Устанавливаем правильный код
                await page.evaluate(f"""
                    monaco.editor.getModels()[0].setValue(`{escaped_code}`);
                """)

                await page.wait_for_timeout(500)

                # Читаем feedback
                feedback = await page.text_content("#feedback")

                success_keywords = ["МАСТЕР ДЕБАГА", "Баг найден", "Исправлено", "ОГОНЬ", "Быстро"]
                if feedback and any(keyword in feedback for keyword in success_keywords):
                    rounds_completed += 1
                    print(f"✅ Раунд {rounds_completed} пройден!")
                    await page.wait_for_timeout(2500)
                else:
                    print(f"❌ Раунд {round_num + 1} не пройден. Feedback: {feedback}")
                    break

            print(f"\n📊 Пройдено раундов: {rounds_completed}")

            # Теперь досрочно завершаем игру
            print("\n🎯 Нажимаем кнопку 'Завершить игру'...")
            finish_btn = await page.query_selector("#finishBtn")
            if finish_btn:
                await finish_btn.click()
                await page.wait_for_timeout(1500)

                # Проверяем финальный экран
                print("\n" + "="*60)
                print("📊 ПРОВЕРКА ФИНАЛЬНОГО ЭКРАНА")
                print("="*60)

                final_screen = await page.query_selector("#finalScreen")
                if final_screen:
                    is_visible = await final_screen.is_visible()
                    print(f"{'✅' if is_visible else '❌'} Финальный экран виден: {is_visible}")

                    if is_visible:
                        # Проверяем отображение количества раундов
                        rounds_text = await page.text_content("#finalRoundsCompleted")
                        print(f"✅ Отображено раундов: {rounds_text}")

                        # Проверяем время
                        time_text = await page.text_content("#finalTimeSpent")
                        print(f"✅ Отображено времени: {time_text}")

                        # Проверяем заголовок
                        title_text = await page.text_content("#finalTitle")
                        print(f"✅ Заголовок: {title_text}")

                        # Проверяем цветовую схему - фиолетовая граница для Bug Hunter
                        border_color = await page.evaluate("""
                            const content = document.querySelector('.final-screen-content');
                            const style = window.getComputedStyle(content);
                            style.borderColor;
                        """)
                        print(f"✅ Цвет границы: {border_color}")

                        # Проверяем, что граница фиолетовая (rgb(139, 47, 201) = #8B2FC9)
                        if "rgb(139, 47, 201)" in border_color or "#8b2fc9" in border_color.lower():
                            print("✅ Цвет границы соответствует теме Bug Hunter (фиолетовый)")
                        else:
                            print(f"⚠️ Цвет границы не фиолетовый: {border_color}")

                        # Делаем скриншот финального экрана
                        await page.screenshot(path="final_screen_bug_hunter.png")
                        print("✅ Скриншот сохранен: final_screen_bug_hunter.png")
                    else:
                        print("❌ Финальный экран НЕ виден!")

                        # Проверяем CSS классы
                        has_show_class = await page.evaluate("""
                            document.getElementById('finalScreen').classList.contains('show');
                        """)
                        print(f"   - Класс 'show' применен: {has_show_class}")

                        # Проверяем display style
                        display_style = await page.evaluate("""
                            const el = document.getElementById('finalScreen');
                            window.getComputedStyle(el).display;
                        """)
                        print(f"   - CSS display: {display_style}")
                else:
                    print("❌ Элемент #finalScreen не найден!")
            else:
                print("❌ Кнопка 'Завершить игру' не найдена!")

            print("\n" + "="*60)
            await page.wait_for_timeout(3000)

        finally:
            await browser.close()


async def main():
    await test_final_screen()


if __name__ == "__main__":
    asyncio.run(main())
