#!/usr/bin/env python3
import asyncio
import json
from playwright.async_api import async_playwright

with open("bugs-data.json", "r", encoding="utf-8") as f:
    BUGS_DATA = json.load(f)

async def test():
    url = "file:///Users/mikhailtrofimov/code/code-typing-game/bug-hunter.html"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(url)
        await page.wait_for_timeout(2000)

        await page.select_option("#languageSelector", value="javascript")
        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)

        # Пройти 3 раунда
        for i in range(3):
            code = BUGS_DATA["javascript"][i]["fixedCode"]
            escaped = code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')
            await page.evaluate(f"monaco.editor.getModels()[0].setValue(`{escaped}`);")
            await page.wait_for_timeout(3000)

        print("🎯 Нажимаем 'Завершить игру'...")
        await page.click("#finishBtn")
        await page.wait_for_timeout(2000)

        is_visible = await page.is_visible("#finalScreen")
        print(f"{'✅' if is_visible else '❌'} Финальный экран виден: {is_visible}")

        if is_visible:
            rounds = await page.text_content("#finalRoundsCompleted")
            time = await page.text_content("#finalTimeSpent")
            title = await page.text_content("#finalTitle")
            msg = await page.text_content("#finalModeMessage")

            print(f"✅ Раундов: {rounds}")
            print(f"✅ Время: {time}")
            print(f"✅ Заголовок: {title}")
            print(f"✅ Сообщение: {msg}")

            # Проверяем цвет
            border = await page.evaluate("""
                window.getComputedStyle(document.querySelector('.final-screen-content')).borderColor
            """)
            print(f"✅ Цвет границы: {border}")

            await page.screenshot(path="final_screen_fixed.png")
            print("✅ Скриншот: final_screen_fixed.png")

        await page.wait_for_timeout(3000)
        await browser.close()

asyncio.run(test())
