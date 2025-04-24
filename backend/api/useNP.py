from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from pydantic import BaseModel

from utility.database import get_students_niepytajki
from utility.database import mark_niepytajka_as_used

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class SerialNumber(BaseModel):
    serialNumber: str = None

@router.post("/useNP")
@limiter.limit("2/second")
async def useNP(request: Request, body: SerialNumber):
    serialNumber = body.serialNumber

    if serialNumber is None or serialNumber == "":
        return JSONResponse(content={"valid": False}, status_code=400)
    
    user_niepytajki = get_students_niepytajki(serialNumber)
    print(user_niepytajki)
    if not user_niepytajki:
        print("Nie znaleziono niepytajki")
    
    if mark_niepytajka_as_used(serialNumber) == 0:
        print("Nie można użyć niepytajki, ponieważ nie ma już żadnej do użycia")
    elif mark_niepytajka_as_used(serialNumber) == 2:
        print("Nie można użyć niepytajki, ponieważ już została użyta dzisiaj")
    else:
        print("Niepytajka została użyta")


