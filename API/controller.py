from fastapi import Request
from fastapi.responses import JSONResponse
from wrappers import transaction
from model import return_db
from foo import get_hashed_password, check_password
from os.path import sep
from const import *
from cryptography.hazmat.primitives import serialization
import datetime
import jwt
import uuid
import pytz
import os


@transaction
async def reg(request: Request):
    db = return_db()
    cookies = request.cookies
    login = str(cookies['login'])
    password = str(cookies['password'])
    mail = str(cookies['mail'])
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
    db.execute_query(
        'INSERT INTO `Users_info` (user_id, contacts) VALUES (%s, %s)', (user_id, mail)
    )
    company_id = db.fetch_query(
        'SELECT `company_id` FROM `Companies` WHERE `owner_id` = %s', (
            user_id,)
    )[0][0]
    db.execute_query(
        'INSERT INTO `Companies_Users` (company_id, user_id) VALUES (%s, %s)', (company_id, user_id))
    return JSONResponse({'status': COMPLETE}, status_code=200)


async def auth(request: Request):
    db = return_db()
    cookies = request.cookies
    login = cookies['login']
    password = cookies['password']
    key = serialization.load_pem_private_key(
        open('private_key.pem', 'rb').read(), password=None)
    try:
        data = db.fetch_query(
            'SELECT `password`, `permissions`, `user_id` FROM Users WHERE login = %s', (login,))[0]
    except IndexError:
        return JSONResponse({'status': FAILURE}, status_code=511)
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
        return JSONResponse({'status': COMPLETE, 'dt': token, 'role': per[permissions], 'company': company}, status_code=200)
    else:
        return JSONResponse({'status': FAILURE}, status_code=511)


@transaction
def mult_execute(request: Request):
    db = return_db()
    cookies = request.cookies
    queryes = cookies[QUERYES]
    token = cookies[TOKEN]
    kk = serialization.load_pem_public_key(
        open('public_key.pem', 'rb').read())
    data = jwt.decode(token, kk, algorithms=["RS256"])
    worker = ('desk_list', 'proj_list', 'task_list', 'task_u', 'worker_list')
    flag = True
    if data['permissions'] in (WORKER, ):
        prem = 'worker'
        for i in [queryes[i][METHOD] for i in queryes]:
            if not i in worker:
                flag = False
                break
    else:
        prem = 'admin'
    if not flag:
        return JSONResponse({'status': FAILURE, 'data': 'Нет доступа к функционалу'})
    for query in queryes:
        method = queryes[query][METHOD]
        kwargs = queryes[query][KWARGS]
        path = f'sql{sep}{prem}{sep}{method}.sql'
        with open(path, 'r') as f:
            sql = f.read()
            foo = sql.strip().sqlit()[0].upper()
            if foo == 'SELECT':
                ans = db.fetch_query(sql, kwargs)
            else:
                db.execute_query(sql, kwargs)
                ans = 'exec_'
    return JSONResponse({'status': COMPLETE, 'data': ans})
