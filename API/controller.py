from fastapi import Request
from fastapi.responses import JSONResponse
from wrappers import transaction
from model import db
from foo import get_hashed_password, check_password
from os.path import sep
from cryptography.hazmat.primitives import serialization
import datetime
import jwt
import uuid
import pytz


@transaction
async def reg(request: Request):
    cookies = request.cookies
    login = str(cookies['login'])
    password = str(cookies['password'])
    uuid3 = uuid.uuid3(uuid.NAMESPACE_DNS, login).__str__()
    db.execute_query(
        'INSERT INTO `Users` (uuid, login, password, permissions) VALUES (%s, %s, %s, %s)', (uuid3,
                                                                                             login,
                                                                                             get_hashed_password(
                                                                                                 password),
                                                                                             2)
    )
    user_id = db.fetch_query(
        'SELECT `user_id` FROM `Users` WHERE `login` = %s', (login, ))[0][0]
    db.execute_query(
        'INSERT INTO `Companies` (owner_id) VALUES (%s)', (user_id, )
    )
    company_id = db.fetch_query(
        'SELECT `company_id` FROM `Companies` WHERE `owner_id` = %s', (
            user_id,)
    )[0][0]
    db.execute_query(
        'INSERT INTO `Companies_Users` (company_id, user_id) VALUES (%s, %s)', (company_id, user_id))
    return JSONResponse({'status': 'complete'}, status_code=200)


per = {'0': 'worker', '1': 'admin', '2': 'superuser'}


async def auth(request: Request):
    cookies = request.cookies
    login = cookies['login']
    password = cookies['password']
    key = serialization.load_pem_private_key(
        open('private_key.pem', 'rb').read(), password=None)
    data = db.fetch_query(
        'SELECT `password`, `permissions`, `user_id` FROM Users WHERE login = %s', (login,))[0]
    password_hash, permissions, user_id = data[0], str(data[1]), data[2]
    company = db.fetch_query(
        'SELECT `company_id` FROM Companies_Users WHERE user_id = %s', (user_id,))[0][0]
    if check_password(password, password_hash):
        token = jwt.encode({'user_id': user_id,
                            'permissions': per[permissions],
                            'company': company,
                            'exp': datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=1)},
                           key,
                           algorithm='RS256')
        kk = serialization.load_pem_public_key(
            open('public_key.pem', 'rb').read())
        print(jwt.decode(token, kk, algorithms=["RS256"]))
        return JSONResponse({'status': 'complete', 'dt': token}, status_code=200)
    else:
        return JSONResponse({'status': 'error'}, status_code=511)


async def get_data():
    pass


async def update():
    pass
