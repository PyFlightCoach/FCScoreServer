import uvicorn
from fastapi import FastAPI, Request, status
import logging

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.middleware.cors import CORSMiddleware
from fcscore.routes import router
import os
from dotenv import load_dotenv
logger = logging.getLogger(__name__)

load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(set(
            ['https://pyflightcoach.github.io', 'http://localhost:5173'] + \
            (os.getenv("CLIENTS").split(",") if 'CLIENTS' in os.environ else [])
        )),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)