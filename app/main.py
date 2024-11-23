from fastapi import FastAPI
from .api.v1.routes.off_recommendations import router as off_recommendation_router
import uvicorn

app = FastAPI()
app.include_router(off_recommendation_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
# @app.get("/")
# async def root():
#     return {"message": "Hello Bigger Applications!"}