from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com", timeout=30000)
    page.screenshot(path="example.png", full_page=True)
    print("✅ Screenshot salvo com sucesso.")
    browser.close()
