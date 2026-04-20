from playwright.sync_api import sync_playwright
import time

def handle_route(route):
    time.sleep(2)
    route.fulfill(status=200, json={"success": True, "fun": 100, "x": [1, 2]})

def run_cuj(page):
    page.goto("http://localhost:5173")
    page.wait_for_timeout(1000)

    # Test IPSolver which requires async operation
    page.get_by_role("tab", name="IP (B&B)").click()
    page.wait_for_timeout(1000)

    # We need to simulate a slow API call. We can do this by mocking the endpoint via Playwright routing.
    page.route("**/api/ip", handle_route)

    # Click submit to start the loading state
    page.get_by_role("button", name="Solve IP").click()
    page.wait_for_timeout(1000)

    # Take screenshot while loading to verify disabled state visually
    page.screenshot(path="/home/jules/verification/screenshots/verification.png")
    page.wait_for_timeout(3000) # Wait for the delayed response to finish

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
