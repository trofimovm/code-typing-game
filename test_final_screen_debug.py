#!/usr/bin/env python3
"""
Debug test для финального экрана
"""
import asyncio
import json
from playwright.async_api import async_playwright, Page

with open("bugs-data.json", "r", encoding="utf-8") as f:
    BUGS_DATA = json.load(f)


async def test_final_screen_debug():
    url = "https://mws-code-game.website.yandexcloud.net/bug-hunter.html"
    language = "javascript"

    print("\n" + "="*60)
    print("🔍 DEBUG ТЕСТ - ФИНАЛЬНЫЙ ЭКРАН")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Обработчик для dialog с логированием
        async def handle_dialog(dialog):
            print(f"🔔 DIALOG ОБНАРУЖЕН: type={dialog.type}, message={dialog.message}")
            await dialog.accept()
            print(f"✅ DIALOG ПРИНЯТ")

        page.on("dialog", handle_dialog)

        # Логирование консольных сообщений
        page.on("console", lambda msg: print(f"🖥️  CONSOLE: {msg.text}"))

        try:
            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            await page.select_option("#languageSelector", value=language)
            print(f"✅ Язык: {language}")

            await page.click('button:has-text("Начать игру")')
            await page.wait_for_timeout(1000)
            print(f"✅ Игра началась")

            # Проходим 3 раунда
            bugs = BUGS_DATA.get(language, [])
            for round_num in range(3):
                bug_index = round_num % len(bugs)
                fixed_code = bugs[bug_index]["fixedCode"]
                escaped_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')

                await page.evaluate(f"""
                    monaco.editor.getModels()[0].setValue(`{escaped_code}`);
                """)
                await page.wait_for_timeout(500)
                feedback = await page.text_content("#feedback")

                if feedback and any(kw in feedback for kw in ["МАСТЕР", "найден", "Исправлено"]):
                    print(f"✅ Раунд {round_num + 1} пройден")
                    await page.wait_for_timeout(2500)

            print("\n🎯 Пытаемся завершить игру...")

            # Проверяем наличие кнопки
            finish_btn_visible = await page.is_visible("#finishBtn")
            print(f"   Кнопка 'Завершить' видна: {finish_btn_visible}")

            # Проверяем gameMode перед завершением
            game_mode = await page.evaluate("gameMode")
            print(f"   gameMode: {game_mode}")

            # Кликаем на кнопку
            print("   Кликаем на #finishBtn...")
            await page.click("#finishBtn")
            print("   Клик выполнен, ждем...")

            # Даем время на обработку dialog и показ финального экрана
            await page.wait_for_timeout(2000)

            # Проверяем результат
            print("\n📊 ПРОВЕРКА ПОСЛЕ КЛИКА:")
            has_show_class = await page.evaluate("""
                document.getElementById('finalScreen').classList.contains('show');
            """)
            print(f"   Класс 'show': {has_show_class}")

            is_visible = await page.is_visible("#finalScreen")
            print(f"   Видимость: {is_visible}")

            display = await page.evaluate("""
                window.getComputedStyle(document.getElementById('finalScreen')).display;
            """)
            print(f"   CSS display: {display}")

            # Проверяем, была ли вызвана showFinalScreen
            # Попробуем вызвать вручную для проверки
            print("\n🔧 Попытка вызвать showFinalScreen() вручную...")
            await page.evaluate("showFinalScreen()")
            await page.wait_for_timeout(1000)

            is_visible_after = await page.is_visible("#finalScreen")
            print(f"   Видимость после ручного вызова: {is_visible_after}")

            if is_visible_after:
                rounds_text = await page.text_content("#finalRoundsCompleted")
                time_text = await page.text_content("#finalTimeSpent")
                title_text = await page.text_content("#finalTitle")
                print(f"   Раундов: {rounds_text}")
                print(f"   Время: {time_text}")
                print(f"   Заголовок: {title_text}")

                # Скриншот
                await page.screenshot(path="final_screen_manual.png")
                print("   Скриншот: final_screen_manual.png")

            await page.wait_for_timeout(3000)

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_final_screen_debug())
