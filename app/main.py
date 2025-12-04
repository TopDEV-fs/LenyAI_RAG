from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# When running `python app/main.py`, the running process's sys.path[0] points
# into the `app` directory. This makes package imports like `import app` fail.
# To make running `python app/main.py` and `uvicorn app.main:app --reload`
# robust, ensure the repository root (parent of `app`) is on sys.path and in
# PYTHONPATH for the reloader subprocesses.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add to PYTHONPATH so uvicorn's reload subprocess can import `app` by name.
py = os.environ.get("PYTHONPATH", "")
if PROJECT_ROOT not in py.split(os.pathsep):
    os.environ["PYTHONPATH"] = os.pathsep.join(
        filter(bool, [PROJECT_ROOT, py])
    )

from app.api.routers import chat
from app.core.config import settings

app = FastAPI(title="LenyAI_RAG - FastAPI Demo")

origins = [
    "http://localhost:5173",  # Example: your frontend application URL
    "https://example.com",    # Allow other origins if necessary
    "http://69.19.136.148:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to LenyAI_RAG FastAPI Demo"}


if __name__ == "__main__":
    # Make running this module as a script (python app/main.py) act like
    # running from the project root so package imports (e.g. `api`, `core`)
    # resolve correctly when the reloader spawns subprocesses.
    import os
    import sys

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Provide a convenient entrypoint for running this script directly during
    # development. We still recommend using `uvicorn app.main:app --reload`.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
