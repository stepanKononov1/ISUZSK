from fastapi import Request
from fastapi.responses import JSONResponse
from wrappers import transaction
from foo import get_hashed_password, check_password, date_serializer
from os.path import sep
from const import *
from cryptography.hazmat.primitives import serialization
import datetime
import jwt
import uuid
import pytz
import json
import os


@transaction
async def reg(request: Request, db):
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


@transaction
async def reg_worker(request: Request, db):
    cookies = request.cookies
    login = str(cookies['login'])
    password = str(cookies['password'])
    per = int(cookies['per'])
    token = str(cookies['dt'])
    kk = serialization.load_pem_public_key(open('public_key.pem', 'rb').read())
    data = jwt.decode(token, kk, algorithms=["RS256"])
    company_id = data['company']
    uuid3 = uuid.uuid3(uuid.NAMESPACE_DNS, login).__str__()
    db.execute_query(
        'INSERT INTO `Users` (uuid, login, password, permissions) VALUES (%s, %s, %s, %s)', (uuid3,
                                                                                             login,
                                                                                             get_hashed_password(
                                                                                                 password),
                                                                                             per)
    )
    age = int(cookies['age'])
    exp = str(cookies['exp'])
    add = str(cookies['add'])
    con = str(cookies['con'])
    name = str(cookies['name'])
    user_id = db.fetch_query(
        'SELECT `user_id` FROM `Users` WHERE `login` = %s', (login, ))[0][0]
    db.execute_query(
        'INSERT INTO `Companies_Users` (company_id, user_id) VALUES (%s, %s)', (company_id, user_id))
    db.execute_query(
        """
        INSERT INTO `Users_info` 
        (`fullname`,
        `age`,
        `experience`,
        `contacts`,
        `add`,
        `user_id`)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, exp, con, add, user_id)
    )
    return JSONResponse({'status': COMPLETE}, status_code=200)


@transaction
async def auth(request: Request, db):
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
async def mult_execute(request: Request, db):
    cookies = request.cookies
    print(cookies[QUERYES])
    queryes = json.loads(cookies[QUERYES])
    token = cookies[TOKEN]
    kk = serialization.load_pem_public_key(
        open('public_key.pem', 'rb').read())
    data = jwt.decode(token, kk, algorithms=["RS256"])
    prem = 'admin'
    ans = {}
    cnt = 0
    for query in queryes:
        req_kw = queryes[query][KWARGS]
        if not isinstance(req_kw[0], list):
            if req_kw[0] == NN:
                kwargs = []
            else:
                kwargs = []
                for i in req_kw:
                    try:
                        if i.startswith(JWT):
                            kwargs.append(data[i.strip(JWT)])
                        elif i.startswith(LASTIND):
                            table_name = i.strip(LASTIND)
                            sql = f'SHOW COLUMNS FROM {table_name}'
                            column = db.fetch_query(sql)[0][0]
                            path = f'sql{sep}{prem}{sep}lastrow.sql'
                            with open(path, 'r') as f:
                                sql = f.read().format(table_name, column)
                                id_row = db.fetch_query(sql)
                                id_row = id_row[0][0]
                            kwargs.append(id_row)
                        else:
                            kwargs.append(i)
                    except AttributeError:
                        kwargs.append(i)
            path = f'sql{sep}{prem}{sep}{query}.sql'
            with open(path, 'r') as f:
                sql = f.read()
                if 'req(company)' in sql:
                    kwargs.append(data['company'])
                foo = sql.strip().split()[0].upper()
                if foo == 'SELECT':
                    if not query == 'lastrow':
                        print(sql, kwargs)
                        ans.update(
                            {f'{query}{cnt}': db.fetch_query(sql, kwargs)})
                    else:
                        sql_show = f'SHOW COLUMNS FROM {kwargs[0]}'
                        column = db.fetch_query(sql_show)[0][0]
                        sql = sql.format(kwargs[0], column)
                        print(sql)
                        ans.update(
                            {f'{query}{cnt}': db.fetch_query(sql)})
                else:
                    print(sql, kwargs)
                    db.execute_query(sql, kwargs)
                    ans.update({f'{query}{cnt}': 'exec_'})
                cnt += 1
        else:
            for j in req_kw:
                kwargs = []
                for i in j:
                    try:
                        if i.startswith(JWT):
                            kwargs.append(data[i.strip(JWT)])
                        elif i.startswith(LASTIND):
                            table_name = i.strip(LASTIND)
                            sql = f'SHOW COLUMNS FROM {table_name}'
                            column = db.fetch_query(sql)[0][0]
                            path = f'sql{sep}{prem}{sep}lastrow.sql'
                            with open(path, 'r') as f:
                                sql = f.read().format(table_name, column)
                                id_row = db.fetch_query(sql)
                                id_row = id_row[0][0]
                            kwargs.append(id_row)
                        else:
                            kwargs.append(i)
                    except AttributeError:
                        kwargs.append(i)
                path = f'sql{sep}{prem}{sep}{query}.sql'
                with open(path, 'r') as f:
                    sql = f.read()
                    if 'req(company)' in sql:
                        kwargs.append(data['company'])
                    foo = sql.strip().split()[0].upper()
                    if foo == 'SELECT':
                        if not query == 'lastrow':
                            ans.update(
                                {f'{query}{cnt}': db.fetch_query(sql, kwargs)})
                        else:
                            sql_show = f'SHOW COLUMNS FROM {kwargs[0]}'
                            column = db.fetch_query(sql_show)[0][0]
                            sql = sql.format(kwargs[0], column)
                            ans.update(
                                {f'{query}{cnt}': db.fetch_query(sql)})
                    else:
                        try:
                            db.execute_query(sql, kwargs)
                            ans.update({f'{query}{cnt}': 'exec_'})
                        except:
                            for k in kwargs:
                                kwg = []
                                for i in k:
                                    try:
                                        if i.startswith(JWT):
                                            kwg.append(data[i.strip(JWT)])
                                        elif i.startswith(LASTIND):
                                            table_name = i.strip(LASTIND)
                                            sl = f'SHOW COLUMNS FROM {table_name}'
                                            column = db.fetch_query(sl)[0][0]
                                            path = f'sql{sep}{prem}{sep}lastrow.sql'
                                            with open(path, 'r') as f:
                                                sl = f.read().format(table_name, column)
                                                id_row = db.fetch_query(sl)
                                                id_row = id_row[0][0]
                                            kwg.append(id_row)
                                        else:
                                            kwg.append(i)
                                    except AttributeError:
                                        kwg.append(i)
                                print(sql, kwg)
                                db.execute_query(sql, kwg)
                                ans.update({f'{query}{cnt}': 'exec_'})
                                cnt += 1
                cnt += 1
    response_data = json.dumps(
        {'status': COMPLETE, 'data': ans}, default=date_serializer)
    return JSONResponse(response_data)
