from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.dtl import DTL
from src.env import getenv

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="app")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/update")
def update_dtl(request: Request):
    global update_requests
    previous_request = update_requests.get(str(request.client), datetime.min)
    if datetime.now() - previous_request < getenv("update_request_interval_limit"):
        return Response(status_code=429)
    else:
        update_requests[str(request.client)] = datetime.now()
        # TODO: clear this map for efficiency
        DTL().update()
        return Response(status_code=200)


@app.get("/")
def get_mainpage(request: Request):
    return templates.TemplateResponse(request=request, name="dtl.html", context={"items": DTL().items_by_tiers})
