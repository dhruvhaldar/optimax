from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5173")

        # Test LP Solver
        page.get_by_label("Objective Coefficients (c):").fill("invalid json")
        page.get_by_role("button", name="Solve LP").click()

        # Wait for error message to appear
        error_locator = page.locator("div[role='alert']")
        expect(error_locator).to_be_visible()

        # Take screenshot of LP Solver error
        page.screenshot(path="verification/lp_error.png")

        # Test Stochastic Solver
        page.get_by_role("button", name="Stochastic Prog").click()
        page.get_by_label("Scenarios (Name, Prob, Yields [Wheat, Corn, Beets]):").fill("bad { json")
        page.get_by_role("button", name="Solve Stochastic LP").click()

        # Wait for error message to appear
        error_locator = page.locator("div[role='alert']")
        expect(error_locator).to_be_visible()

        # Take screenshot of Stochastic Solver error
        page.screenshot(path="verification/stochastic_error.png")

        browser.close()

if __name__ == "__main__":
    run()
