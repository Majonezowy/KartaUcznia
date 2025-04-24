from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from utility.database import get_user, get_students_niepytajki

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/check-validity")
@limiter.limit("3/second")
async def check_validity(request: Request, serialNumber: str = None):
    if not serialNumber:
        return JSONResponse(content={"valid": False, "message": "Serial number is required."}, status_code=400)
    
    user = get_user(serialNumber)
    if not user:
        return JSONResponse(content={
            "name": "Nie znaleziono",
            "valid": False,
            "used": False,
            "user_role": "guest",
            "message": "User not found."
        }, status_code=200)
    
    user_niepytajki = get_students_niepytajki(serialNumber)
    if not user_niepytajki:
        return create_user_response(user, valid=False, used=False)
    
    if user[4] != "student":
        return create_user_response(user, valid=False, used=False)
    
    used_today = get_students_niepytajki(serialNumber)
    return create_user_response(user, valid=True, used=used_today)

def create_user_response(user, valid: bool, used: bool):
    return JSONResponse(content={
        "name": f"{user[2]} {user[3]}",
        "valid": valid,
        "used": used,
        "user_role": user[4]
    }, status_code=200)
