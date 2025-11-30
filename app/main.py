from app.routers import user, emotion_router
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from ai-buddy backend!"}
app.include_router(user.router)
app.include_router(emotion_router.router)
