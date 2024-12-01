# app/main.py
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from app.api.v1.routes.off_recommendations import router
from contextlib import asynccontextmanager
from dependencies import get_dataset_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    dataset_manager = get_dataset_manager()
    dataset_manager.initialize_dataset()
    yield
    # Shutdown
    dataset_manager.clear_cache()

app = FastAPI(lifespan=lifespan)


app.include_router(
    router,
    dependencies=[Depends(get_dataset_manager)]
)

@app.get("/health")
async def health_check():
    dataset_manager = get_dataset_manager()
    health_status = dataset_manager.health_check()
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)