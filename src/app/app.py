from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.env import getenv
from src.utils import get_dtl, update_dtl

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="app", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

update_requests = {}


@app.post("/update")
def refresh_tierlist(request: Request):
    global update_requests
    # clear expired records
    records = update_requests.items()
    for client, request_time in records:
        if datetime.now() - request_time >= getenv("update_request_interval_limit"):
            update_requests.pop(client)
    if str(request.client.host) in update_requests:
        return Response(status_code=429)
    update_requests[str(request.client.host)] = datetime.now()
    update_dtl()
    return Response(status_code=200)


@app.get("/")
def get_tierlist(request: Request):
    return templates.TemplateResponse(request=request, name="dtl.html", context={"dtl": get_dtl()})


@app.get("/rules")
def get_rules(request: Request):
    return templates.TemplateResponse(request=request, name="rules.html")
