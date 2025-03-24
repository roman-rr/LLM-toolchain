from fastapi import APIRouter
from api.v1.endpoints.file_upload import router as file_router
# from api.v1.endpoints.llm import router as llm_router

# Create the main API router
api_router = APIRouter()

# Include routers from endpoints with their prefixes and tags
api_router.include_router(
    file_router,
    prefix="/files",
    tags=["Files"]
)

# api_router.include_router(
#     llm_router,
#     prefix="/llm",
#     tags=["LLM"]
# )

# You can add more routers here as your API grows 