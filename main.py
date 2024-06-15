import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from fcscore.routes import router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    origins = [
        "http://localhost:5173",
        "http://localhost:4173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)