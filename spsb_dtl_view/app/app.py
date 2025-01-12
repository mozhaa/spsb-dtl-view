from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()


@app.get("/")
def get_mainpage(request: Request):
    return templates.TemplateResponse(request=request, name="dtl.html")
