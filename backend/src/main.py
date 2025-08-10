from fastapi import FastAPI
from src.modules.auth.controller import router as auth_router
from src.modules.citizens.controller import router as citizens_router
from src.modules.meetings.controller import router as meetings_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(citizens_router)
app.include_router(meetings_router)
