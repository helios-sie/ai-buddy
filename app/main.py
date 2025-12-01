from fastapi import FastAPI

# Routers
from app.routers.user import router as user_router
from app.routers.emotion_router import router as emotion_router
from app.routers.chat_router import router as chat_router

app = FastAPI(
    title="AI Buddy Backend",
    version="1.0.0",
    description="Backend for emotional companion AI with memory + personality engine"
)


@app.get("/")
def read_root():
    return {"message": "Hello from ai-buddy backend!"}


# Register Routers
app.include_router(user_router)
app.include_router(emotion_router)
app.include_router(chat_router)
