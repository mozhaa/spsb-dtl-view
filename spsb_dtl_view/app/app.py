from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from spsb_dtl_view.parse import DTL

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="app")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def get_mainpage(request: Request):
    return templates.TemplateResponse(request=request, name="dtl.html", context={"items": DTL().items})
