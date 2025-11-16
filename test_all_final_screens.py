#!/usr/bin/env python3
"""
Тестирование финальных экранов всех трёх игр
"""
import asyncio
import json
from playwright.async_api import async_playwright

with open("bugs-data.json", "r", encoding="utf-8") as f:
    BUGS_DATA = json.load(f)


async def test_bug_hunter():
    """Тестирует Bug Hunter"""
    print("\n" + "="*60)
    print("🐛 КОД-ХАНТИНГ")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("dialog", lambda d: asyncio.create_task(d.accept()))

        await page.goto("https://mws-code-game.website.yandexcloud.net/bug-hunter.html")
        await page.wait_for_timeout(2000)

        await page.select_option("#languageSelector", value="javascript")
        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)

        # Пройти 2 раунда
        for i in range(2):
            code = BUGS_DATA["javascript"][i]["fixedCode"]
            escaped = code.replace('`', '\\`').replace('${', '\\${').replace('\\', '\\\\')
            await page.evaluate(f"monaco.editor.getModels()[0].setValue(`{escaped}`);")
            await page.wait_for_timeout(3000)

        await page.click("#finishBtn")
        await page.wait_for_timeout(1500)

        is_visible = await page.is_visible("#finalScreen")
        rounds = await page.text_content("#finalRoundsCompleted")
        border = await page.evaluate("window.getComputedStyle(document.querySelector('.final-screen-content')).borderColor")

        print(f"{'✅' if is_visible else '❌'} Финальный экран виден: {is_visible}")
        print(f"✅ Раундов пройдено: {rounds}")
        print(f"✅ Цвет границы: {border}")
        print(f"{'✅' if 'rgb(139, 47, 201)' in border else '❌'} Соответствует фиолетовой теме")

        await browser.close()
        return is_visible


async def test_speed_typing():
    """Тестирует Скоростной набор"""
    print("\n" + "="*60)
    print("⚡ СКОРОСТНОЙ НАБОР")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("dialog", lambda d: asyncio.create_task(d.accept()))

        await page.goto("https://mws-code-game.website.yandexcloud.net/speed-typing.html")
        await page.wait_for_timeout(1000)

        # Начать игру и дождаться появления кода
        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)

        # Получить код для печати и ввести его
        target_code = await page.evaluate("currentTargetCode")
        await page.evaluate(f"monaco.editor.getModels()[0].setValue(`{target_code}`);")
        await page.wait_for_timeout(3000)

        # Завершить игру
        await page.click("#finishBtn")
        await page.wait_for_timeout(1500)

        is_visible = await page.is_visible("#finalScreen")
        if is_visible:
            rounds = await page.text_content("#finalRoundsCompleted")
            border = await page.evaluate("window.getComputedStyle(document.querySelector('.final-screen-content')).borderColor")

            print(f"✅ Финальный экран виден: {is_visible}")
            print(f"✅ Раундов пройдено: {rounds}")
            print(f"✅ Цвет границы: {border}")
            print(f"{'✅' if 'rgb(255, 0, 50)' in border else '❌'} Соответствует красной теме")
        else:
            print(f"❌ Финальный экран НЕ виден!")

        await browser.close()
        return is_visible


async def test_cloud_architect():
    """Тестирует Cloud Architect"""
    print("\n" + "="*60)
    print("🏗️ ТЕКИ LOW-КОДИНГ")
    print("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("dialog", lambda d: asyncio.create_task(d.accept()))

        await page.goto("https://mws-code-game.website.yandexcloud.net/cloud-architect.html")
        await page.wait_for_timeout(1000)

        await page.click('button:has-text("Начать игру")')
        await page.wait_for_timeout(1000)

        # Просто завершить сразу для проверки экрана
        await page.click("#finishBtn")
        await page.wait_for_timeout(1500)

        is_visible = await page.is_visible("#finalScreen")
        if is_visible:
            rounds = await page.text_content("#finalRoundsCompleted")
            border = await page.evaluate("window.getComputedStyle(document.querySelector('.final-screen-content')).borderColor")

            print(f"✅ Финальный экран виден: {is_visible}")
            print(f"✅ Раундов пройдено: {rounds}")
            print(f"✅ Цвет границы: {border}")
            print(f"{'✅' if 'rgb(136, 136, 136)' in border else '⚠️'} Соответствует серой теме")
        else:
            print(f"❌ Финальный экран НЕ виден!")

        await browser.close()
        return is_visible


async def main():
    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║     Проверка финальных экранов всех игр                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    results = {
        "Bug Hunter": await test_bug_hunter(),
        "Speed Typing": await test_speed_typing(),
        "Cloud Architect": await test_cloud_architect()
    }

    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("="*60)

    for game, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {game}: {'Финальный экран работает' if success else 'ОШИБКА'}")

    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ВСЕ ФИНАЛЬНЫЕ ЭКРАНЫ РАБОТАЮТ КОРРЕКТНО!")
    else:
        print("⚠️ Некоторые финальные экраны требуют исправления")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
