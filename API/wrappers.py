from fastapi.responses import JSONResponse
from mysql.connector.errors import ProgrammingError
from const import FAILURE
from model import return_db


from fastapi.responses import JSONResponse
from mysql.connector.errors import ProgrammingError
from const import FAILURE
from model import return_db


def transaction1(foo):
    async def wrapper(*args, **kwargs):
        db = return_db()
        # Начинаем транзакцию
        db.start_transaction()
        # Выполняем саму функцию
        responce = await foo(*args, db=db, **kwargs)

        # Если функция вызвала ошибку, выводим её в консоль
        if not responce:
            print("Error occurred during function execution")
            db.rollback()
            responce = JSONResponse(
                {'status': FAILURE, 'data': 'Непредвиденная ошибка'}, status_code=409
            )
        else:
            db.commit()  # Если ошибок нет, коммитим транзакцию

        return responce

    return wrapper


def transaction(foo):
    async def wrapper(*args, **kwargs):
        db = return_db()
        try:
            db.start_transaction()
        except ProgrammingError:
            print(e)
            responce = JSONResponse(
                {'status': FAILURE, 'data': 'Произошла ошибка сервера, повторите позже'}, status_code=409)
            db.rollback()
        except Exception as e:
            print(e)
            responce = JSONResponse(
                {'status': FAILURE, 'data': 'Непредвиденная ошибка'}, status_code=409
            )
        try:
            responce = await foo(*args, db=db, **kwargs)
        except Exception as e:
            print(e)
            responce = JSONResponse(
                {'status': FAILURE, 'data': 'Непредвиденная ошибка'}, status_code=409)
            db.rollback()
        finally:
            db.commit()
        return responce
    return wrapper
