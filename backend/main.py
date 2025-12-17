from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
frontend_url = os.getenv("FRONTEND_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from api.auth_routes import auth_router
from api.chat_routes import chat_router
from api.user_routes import user_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(user_router)