from playwright.sync_api import sync_playwright, expect

def verify_shortcut():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the local dev server
        print("Navigating to app...")
        page.goto("http://localhost:5173")

        # Wait for the solver to load (handle lazy loading)
        print("Waiting for solver to load...")
        expect(page.get_by_text("Linear Programming Solver")).to_be_visible(timeout=10000)

        # Find the Solve button and check for the shortcut hint
        solve_button = page.get_by_role("button", name="Solve LP ⌘↵")
        expect(solve_button).to_be_visible()
        print("Shortcut hint visible.")

        # Focus on an input field
        print("Focusing input...")
        page.get_by_label("Objective Coefficients (c):").click()

        # Press Control+Enter
        print("Pressing Control+Enter...")
        page.keyboard.press("Control+Enter")

        # Verify that the button enters loading state OR shows error OR shows results
        # Since we don't have a backend running, it might fail or stay loading.
        # But the UI state change is what we want to verify.

        # Check for "Solving..." text which indicates the function was called
        print("Verifying loading state...")
        expect(page.get_by_text("Solving...")).to_be_visible(timeout=5000)

        # Take a screenshot of the loading state
        print("Taking screenshot...")
        page.screenshot(path="verification/lp_shortcut_loading.png")

        browser.close()
        print("Verification complete!")

if __name__ == "__main__":
    verify_shortcut()
