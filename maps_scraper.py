import asyncio
import sys
from playwright.sync_api import sync_playwright
import logging

# Windows asyncio fix for Playwright
if sys.platform == 'win32':
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logger = logging.getLogger(__name__)

def scrape_google_maps(industry, location, max_results=50, update_func=None):
    query = f"{industry} in {location}"
    search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    
    results = []
    
    def log_update(msg):
        if update_func:
            update_func(msg)
        logger.info(msg)

    try:
        with sync_playwright() as p:
            log_update("Initializing Playwright...")
            try:
                # Use --no-sandbox and other flags for Cloud/Linux compatibility
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
            except Exception as e:
                if "executable" in str(e).lower() or "not found" in str(e).lower():
                    log_update("Browsers not found. Attempting to install...")
                    import os
                    os.system("playwright install chromium")
                    browser = p.chromium.launch(
                        headless=True,
                        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                    )
                else:
                    raise e

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            log_update(f"Navigating to Google Maps for '{query}'...")
            page.goto(search_url, timeout=60000)
            
            # Wait for the sidebar to load
            try:
                page.wait_for_selector('role=main', timeout=20000)
                log_update("Search results loaded. Starting data collection...")
            except:
                log_update("Error: Could not find results sidebar. Maps might be blocking or query is invalid.")
                browser.close()
                return []

        processed_names = set()
        scroll_attempts = 0
        max_scroll_attempts = 15 # Safety limit
        consecutive_same_count = 0
        last_results_count = 0
        
        while len(results) < max_results and scroll_attempts < max_scroll_attempts:
            containers = page.query_selector_all("div[role='article']")
            current_count = len(containers)
            
            log_update(f"Scanning view: {current_count} items found.")
            
            # If we see the same number of items multiple times, Google Maps might be stuck or at the end
            if current_count == last_results_count:
                consecutive_same_count += 1
            else:
                consecutive_same_count = 0
            
            last_results_count = current_count
            
            if consecutive_same_count >= 3:
                log_update("No new results appearing after multiple scrolls. Stopping.")
                break

            for container in containers:
                try:
                    name_el = container.query_selector("div.fontHeadlineSmall")
                    if not name_el: continue
                    name = name_el.inner_text()
                    
                    if name in processed_names:
                        continue
                        
                    processed_names.add(name)
                    
                    # Website detection
                    website = "NO_WEBSITE"
                    web_el = container.query_selector("a[aria-label*='website']")
                    if web_el:
                        href = web_el.get_attribute("href")
                        if href: website = href
                    
                    results.append({
                        "company_name": name,
                        "google_maps_link": page.url,
                        "website_url": website,
                        "phone_number": "N/A"
                    })
                    
                    if len(results) >= max_results:
                        break
                except Exception:
                    continue
            
            if len(results) >= max_results:
                break

            # Scroll logic
            if containers:
                scroll_attempts += 1
                log_update(f"Scrolling down... (Attempt {scroll_attempts}/{max_scroll_attempts})")
                containers[-1].scroll_into_view_if_needed()
                page.wait_for_timeout(3000)
            else:
                break

            # End of list check
            if page.query_selector("text='You've reached the end of the list'"):
                log_update("Reached the absolute end of the list.")
                break

        log_update(f"Collection complete. Found {len(results)} raw leads.")
        browser.close()
        
    except Exception as e:
        log_update(f"Critical Scraper Error: {str(e)}")
        return []

    return results
