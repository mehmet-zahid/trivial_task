import re
from typing import List, Tuple
from io import BytesIO
from PIL import Image
import aiohttp
import re
from bs4 import BeautifulSoup

url_pattern = re.compile(r'^(https?://)?[a-z0-9-]+(\.[a-z0-9-]+)+([/?].*)?$')

class NotPassedTest(Exception):
    pass

def filter_urls(urls: str) -> Tuple[List[str], List[str]]:
    valid_urls = []
    invalid_urls = []
    url_list = urls.split('\r\n')
    for url in url_list:
        if not url_pattern.match(url):
            invalid_urls.append(url)
        else:
            valid_urls.append(url)
        
    return valid_urls, invalid_urls

def validate_url(url):
    if not url_pattern.match(url):
        return False
    return True



async def check_urls(urls: List[str]) -> List[tuple]:
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            res: List[str,str,str] = []
            # check for valid URL format
            if not re.match(r"^https?://", url):
                results.append((url,"INVALID_URL"))
                continue

            # try to fetch page and check response
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        results.append({"url": url, "status": "INVALID_RESPONSE"})
                        continue
                    else:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")

                        # check if images have high enough resolution
                        img_tags = soup.find_all("img")
                        for img_tag in img_tags:
                            img_url = img_tag.get("src")
                            if img_url.startswith("http"):
                                async with session.get(img_url) as img_response:
                                    if img_response.status != 200:
                                        results.append({"url": url, "status": "INVALID_IMAGE_RESOLUTION"})
                                        break
                                    else:
                                        img_data = await img_response.content.read()
                                        img_width, img_height = get_image_dimensions(img_data)
                                        if img_width < 800 or img_height < 600:
                                            results.append({"url": url, "status": "INVALID_IMAGE_RESOLUTION"})
                                            break

                        # check for proper page content
                        if not soup.find(text="Class Central"):
                            results.append({"url": url, "status": "INVALID_PAGE_CONTENT"})
                            continue

                        # check if JavaScript dropdown is working properly
                        if not soup.find("select", attrs={"id": "select-institution"}):
                            results.append({"url": url, "status": "INVALID_JAVASCRIPT"})
                            continue

                        results.append({"url": url, "status": "PASS"})

            except:
                results.append({"url": url, "status": "INVALID_REQUEST"})

    return results

def get_image_dimensions(image_data):
    """
    Helper function to get the dimensions of an image from its data.
    """
    with Image.open(BytesIO(image_data)) as img:
        return img.size



async def test_url(urls: List[str]) -> List[dict]:
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            res: dict = {"url": url, "PASS": True, "message": []}
            #if not validate_url(url):
            #    res['message'].append("INVALID_URL")
            #    res['description'] = "Invalid URL format"
            #    continue


            try:
                async with session.get(url) as response:
                    
                    if response.status != 200:
                        res['message'].append("INVALID_RESPONSE")
                        #res['description'] = "status code not 200"
                        res['PASS'] = False
                        raise NotPassedTest("INVALID_RESPONSE")
                    
                    soup = BeautifulSoup(await response.content.read(), 'html.parser')

                    # Test for inner pages not translated
                    lang_links = soup.find_all(href=re.compile("/translate"))
                    if lang_links:
                        res['message'].append("Inner pages not translated")

                    # Find all links on the page
                    links = soup.find_all('a')

                    # Loop through all links and check if the href attribute contains 'hi'
                    for link in links:
                        href = link.get('href')
                        if href:
                            if not 'hi' in href:
                                res['message'].append(f"The page {href} has not been translated to Hindi")
                                break

                    # Test for images not high resolution
                    img_tags = soup.find_all("img")
                    for tag in img_tags:
                        src = tag.get("src")
                        if src and not src.startswith("data:image") and not src.startswith("http"):
                            img_resp = await session.get(response.url.join(src))
                            if img_resp.headers.get("Content-Length") and int(img_resp.headers["Content-Length"]) > 100_000:
                                res['message'].append("Images not high resolution")
                                raise NotPassedTest("Images not high resolution")

                    # Test for javascript dropdown not working properly
                    js_dropdowns = soup.find_all(class_=re.compile("(?i)dropdown|select2"))
                    for dropdown in js_dropdowns:
                        if "disabled" not in dropdown.attrs.get("class", []):
                            dropdown_options = dropdown.select("option")
                            if len(dropdown_options) <= 1:
                                res['message'].append("Javascript dropdown not working properly")
                                raise NotPassedTest("Javascript dropdown not working properly")
                            
            except NotPassedTest as e:
                res['PASS'] = False
                print(e)
                                
            except Exception as e:
                res['note'] = ["INVALID_REQUEST"]
                res['description'] = "exception raised"
                res['PASS'] = False
                print(e)
            
            results.append(res)
    print(results)
    return results