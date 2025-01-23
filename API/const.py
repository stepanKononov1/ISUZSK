COMPLETE = 'complete'
FAILURE = 'fail'
UNAUTH = 'unauth'
UNPREM = 'unprem'
ADMIN = 'a'
OWNER = 'o'
WORKER = 'w'


per = {'0': WORKER, '1': ADMIN, '2': OWNER}
re_per = {WORKER: 0, ADMIN: 1, OWNER: 2}
