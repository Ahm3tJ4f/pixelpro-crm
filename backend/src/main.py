from fastapi import FastAPI
from src.modules.auth.controller import router as auth_router

app = FastAPI()

app.include_router(auth_router)
