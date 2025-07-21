#app.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the app instances from your other files
# Make sure the filenames are correct. I'm using "Analyis.py" as you provided.

from analysis import analysis_app
from gen import generation_app

# Create the main, top-level application
app = FastAPI(
    title="Unified Code Conversion API",
    description="A single API to handle repository analysis and project generation.",
    version="1.0.0"
)

# Add CORS middleware to the main app. This will apply to all sub-apps.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be more specific in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Mount the sub-applications ---

# Mount the analysis service under the "/api/analyze" path prefix
app.mount("/api/analyze", analysis_app)

# Mount the generation service under the "/api/generate" path prefix
app.mount("/api/generate", generation_app)


# --- Add a root endpoint to the main app for a health check ---
@app.get("/")
def read_root():
    """
    Root endpoint for the unified API.
    Provides links to the sub-application docs.
    """
    return {
        "message": "Welcome to the Unified Code Conversion API",
        "documentation": "/docs",
        "analysis_api_docs": "/api/analyze/docs",
        "generation_api_docs": "/api/generate/docs"
    }


# --- Main entry point to run the entire unified application ---
if __name__ == "__main__":
    print("Starting the Unified FastAPI server on http://0.0.0.0:8000")
    # We run the main 'app' instance from this file
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)