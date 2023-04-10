from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from typing import List
from helper import test_url
#from extract import check_urls


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def submit_url(request: Request, urls: str = Form(default="")):
    #valid_urls, invalid_urls = validate_urls(urls)
    results_list = await test_url(urls.splitlines())
    print(results_list)
    return templates.TemplateResponse("results2.html", {"request": request, "results_list": results_list})
    #return templates.TemplateResponse("url_validation.html", {"request": request, "valid_urls": valid_urls, "invalid_urls": invalid_urls})
    

APP_PORT = os.getenv('APP_PORT')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(APP_PORT if APP_PORT else '8000'))    