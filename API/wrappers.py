from fastapi.responses import JSONResponse
from model import db


def transaction(foo):
    async def wrapper(*args, **kwargs):
        db.start_transaction()
        try:
            responce = await foo(*args, **kwargs)
        except Exception as e:
            print(e)
            responce = JSONResponse(
                {'error': 'transaction failed'}, status_code=409)
            db.rollback()
        finally:
            db.commit()
        return responce
    return wrapper
