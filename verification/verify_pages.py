from playwright.sync_api import sync_playwright

def verify_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to index.html
        print("Navigating to index.html...")
        page.goto("http://localhost:8000/index.html")
        page.screenshot(path="verification/index.png")
        print("Captured index.png")
        
        # Click the link for Laptops
        print("Clicking 'Las 10 Mejores Laptops...'")
        # The card has h3 with text, and a button. The button is the link.
        # But the h3 is inside the article card.
        # Let's find the link with href="laptops-programar.html"
        
        with page.expect_navigation():
            page.click('a[href="laptops-programar.html"]')
            
        # Verify we are on the new page
        print(f"Current URL: {page.url}")
        if "laptops-programar.html" not in page.url:
            print("ERROR: Did not navigate to laptops-programar.html")
        
        # Take screenshot of the article page
        page.screenshot(path="verification/article.png")
        print("Captured article.png")
        
        # Verify H1 (The second h1 on the page, first is site title)
        # Using specific selector .article-header h1
        h1_text = page.inner_text(".article-header h1")
        print(f"Article H1: {h1_text}")
        
        if "Las 10 Mejores Laptops para Programar en 2024" not in h1_text:
             print("ERROR: H1 text mismatch")

        browser.close()

if __name__ == "__main__":
    verify_pages()
