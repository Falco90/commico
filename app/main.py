from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.core.settings import settings
from app.api import auth
from app.core.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()   # optional — see note below
    yield
    # Shutdown (nothing for now)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # frontend
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)

    return app

app = create_app()

