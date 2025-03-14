import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.env import getenv
from src.utils import get_dtl, update_dtl

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="app", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

previous_update = datetime.min
previous_update_lock = asyncio.Lock()


@app.post("/update")
async def refresh_tierlist(request: Request):
    global previous_update
    async with previous_update_lock:
        if datetime.now() - previous_update < getenv("update_request_interval_limit"):
            return Response(status_code=429)
        previous_update = datetime.now()
    update_dtl()
    return Response(status_code=200)


@app.get("/")
def get_tierlist(request: Request):
    return templates.TemplateResponse(request=request, name="dtl.html", context={"dtl": get_dtl()})


@app.get("/rules")
def get_rules(request: Request):
    return templates.TemplateResponse(request=request, name="rules.html")
