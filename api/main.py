from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Use relative import for router
from .v1.router import api_router
# Use absolute import for settings since it's outside api folder
from config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for file uploads and LLM operations",
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

if __name__ == "__main__":
    import uvicorn
    # Use the correct module path
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG) 