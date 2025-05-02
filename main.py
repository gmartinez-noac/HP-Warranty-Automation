import re
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError
import time

# Opens a new tab and inputs serial number
def submit_serial(page, serial_number, close_popup=False):
    page.goto("https://support.hp.com/us-en/check-warranty")

    # On the first tab, a pop up will appear
    if close_popup:
        try:
            popup = page.get_by_role("button", name="Close", exact=True)
            popup.wait_for(state="visible", timeout=3000)
            popup.click()
        except TimeoutError:
            print("Popup did not appear within 3 seconds. Continuing...")
    
    serial_input = page.get_by_placeholder("Example: HU265BM18V")
    serial_input.click()
    serial_input.fill(serial_number)
    page.get_by_role("button", name="Submit").click()

# In some cases, the serial number is not enough to verify warranty status
# If so, a second textbox will appear asking for a product number
def handle_product_number(page, product_number=None):
    try:
        product_input = page.get_by_placeholder("Example: 7NM78PA")
        product_input.wait_for(state="visible", timeout=2500)
        if product_number:
            print(f"Filling product number: {product_number}")
            product_input.fill(product_number)
            page.get_by_role("button", name="Submit").click()
        else:
            print("Product number required, but none provided.")
    except TimeoutError:
        print("No product number field appeared, serial was accepted.")

def run_batch(context, serials_and_products):
    pages = []

    # Submit all serial numbers first
    for i, (serial, _) in enumerate(serials_and_products):
        page = context.new_page()
        submit_serial(page, serial, close_popup=(i == 0))
        pages.append(page)

    # After all tabs are submitted, go through again to handle product number
    for page, (_, product_number) in zip(pages, serials_and_products):
        handle_product_number(page, product_number)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)

    # --------- First Window ---------
    context1 = browser.new_context()
    batch1 = [
        ("2MQ4510CMH", None),
        ("2MQ4510CZ6", None),
        ("2MQ4510J8H", None),
        ("2MQ4510JCF", None),
        ("2MQ4510JDH", None),
        ("2MQ4510J79", None),
        ("2MQ4510J88", None)
    ]
    
    run_batch(context1, batch1)

    # --------- Second Window ---------
    # context2 = browser.new_context()
    # batch2 = [
    #     ("CND5140NW5", "8Z8L6AV"),
    #     ("CND5140NW6", "8Z8L6AV"),
    #     ("CND5140J0M", "8Z8L6AV"),
    #     ("CND5140NW4", "8Z8L6AV"),
    #     ("CND5140J0J", "8Z8L6AV"),
    #     ("CND5140J0P", "8Z8L6AV")
    # ]
    # 
    # run_batch(context2, batch2)



    time.sleep(1000)

    # ---------------------
    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
