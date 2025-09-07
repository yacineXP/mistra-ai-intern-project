import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.v1 import analysis

app = FastAPI(
    title="AI Data Analyst",
    description="An API for analyzing CSV data using natural language.",
    version="1.0.0"
)

app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])

dist_folder = os.path.join(os.path.dirname(__file__), "..", "dist")

app.mount("/assets", StaticFiles(directory=dist_folder), name="assets")

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_root():
    """
    Serves the main index.html file from the distribution ('dist') folder.
    This is the entry point for the user interface.
    """
    index_path = os.path.join(dist_folder, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built. Please run 'python build.py'"}

