from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, chat
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="HR Internal Q&A System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR + "/admin", tags=["admin"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])


@app.get("/")
def read_root():
    return {"message": "HR Internal Q&A System API", "version": settings.VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}