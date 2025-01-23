from fastapi.responses import JSONResponse
from mysql.connector.errors import ProgrammingError
from const import FAILURE
from model import return_db


def transaction(foo):
    async def wrapper(*args, **kwargs):
        db = return_db()
        try:
            db.start_transaction()
        except ProgrammingError:
            responce = JSONResponse(
                {'status': FAILURE, 'text': 'Произошла ошибка сервера, повторите позже'}, status_code=409)
            db.rollback()
        except Exception as e:
            responce = JSONResponse(
                {'status': FAILURE, 'text': 'Непредвиденная ошибка'}, status_code=409
            )
        try:
            responce = await foo(*args, **kwargs)
        except Exception as e:
            print(e)
            responce = JSONResponse(
                {'status': FAILURE, 'text': 'Непредвиденная ошибка'}, status_code=409)
            db.rollback()
        finally:
            db.commit()
        return responce
    return wrapper
