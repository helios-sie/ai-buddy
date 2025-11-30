from fastapi import APIRouter

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/test")
def test_user():
    return {"message": "User router working!"}
