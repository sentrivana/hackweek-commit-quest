from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from commitquest.routers import api, views


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api.router)
app.include_router(views.router)
