from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from requests_html import AsyncHTMLSession, HTML
from bs4 import BeautifulSoup


driver_path = os.path.join(os.getcwd(), "chromedriver")

def createDriver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    prefs = {"profile.managed_default_content_settings.images":2}
    chrome_options.headless = True

    
    chrome_options.add_experimental_option("prefs", prefs)
    myDriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return myDriver

def getGoogleHomepage(driver: webdriver.Chrome) -> str:
    driver.get("https://www.google.com")
    return driver.page_source

def doBackgroundTask(inp):
    print("Doing background task")
    print(inp.msg)
    print("Done")


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
    
        
