from playwright.sync_api import sync_playwright

def filling (url, name, phoneNumber, date):
    with sync_playwright() as p:
        # Launch browser in headless mode for server efficiency
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Click the 'Celebrate' CTA button

        page.wait_for_timeout(1000)
        page.query_selector('a.layout_69771adf29588').click(force=True)
        page.wait_for_timeout(1000)

        # Fill out the form fields

        page.fill('.field-type-text .form-control', name)
        page.fill('.field-type-tel .form-control', phoneNumber)
        page.fill('input.date_picker', date)

        # Select marketing source and capture proof

        page.select_option('select.form-select', label='Telegram')
        page.screenshot(path='FilledForms.png')

        browser.close()

# Data to test function: filling('https://kyiv.epiland.com', 'Роман', '0689334547', '18.04.2026')