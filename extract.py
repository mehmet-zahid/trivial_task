from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    
import os
import time
from requests_html import AsyncHTMLSession, HTML
from bs4 import BeautifulSoup
import requests
from helper import validate_url

class NotPassedTest(Exception):
    pass
#driver_path = os.path.join(os.getcwd(), "chromedriver")

def createDriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = { 'performance':'ALL' }
    
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.headless = True

    
    chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options, service_args=["--verbose", f"--log-path={os.path.join(os.getcwd(), 'chromedriverxx.log')}"], desired_capabilities=d)

    return myDriver

def test_url(urls):
    results = []
    driver = createDriver()

    for url in urls:
        res = {"url": url, "PASS": True, "message": [], "description": ""}
        if not validate_url(url):
            res['message'].append("INVALID_URL")
            res['description'] = "Invalid URL format"
            res['PASS'] = False
            

        try:
            driver.get(url)
            if requests.get(driver.current_url).status_code != 200:
                res['message'].append("INVALID_RESPONSE_CODE")
                res['description'] = "response status code not 200"
                res['PASS'] = False
                raise NotPassedTest("INVALID_RESPONSE")
            
            
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # wait until the page loads

            
            
            # Test for inner pages not translated
            lang_links = driver.find_elements(by=By.XPATH, value="//a[contains(@href,'/translate')]")
            if lang_links:
                res['message'].append("Inner pages not translated")
                res['PASS'] = False

            # Test for images not high resolution
            img_tags = driver.find_elements(by=By.TAG_NAME, value="img")
            for tag in img_tags:
                src = tag.get_attribute("src")
                if src and not src.startswith("data:image") and not src.startswith("http"):
                    img_size = int(tag.get_attribute("naturalWidth")) * int(tag.get_attribute("naturalHeight"))
                    if img_size > 100_000:
                        res['message'].append("Images not high resolution")
                        break
            
            # Test for javascript dropdown not working properly
            js_dropdowns = driver.find_elements(by=By.TAG_NAME, value="select")
            
            for dropdown in js_dropdowns:
                sel = Select(dropdown) # select_by_index(1)
                
                if sel.options:
                    for i, option in enumerate(sel.options):
                        try:
                            if option.is_enabled():
                                print(sel.select_by_index(i))
                                time.sleep(0.5)
                        except Exception as e:
                            print(e)                            
                            res['message'].append("Not all dropdown working properly")
                            break
        
        except Exception as e:
            res['message'].append("INVALID_REQUEST")
            res['description'] = "exception raised"
            res['PASS'] = False
            print(e)

        results.append(res)

    driver.quit()
    return results


async def check_urls(urls: list) -> dict:
    results = {}
    asession = AsyncHTMLSession()
    
    for url in urls:
        try:
            response = await asession.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string
            results[url] = {"status": "success", "title": title}
            
        except Exception as e:
            results[url] = {"status": "failed", "error": str(e)}
    
    return results
    
        
