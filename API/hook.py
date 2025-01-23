from fastapi import FastAPI, Request
from dotenv import dotenv_values
import controller as connt
import uvicorn

config = dotenv_values('.env')
app = FastAPI()


@app.post('/registration')
async def reg(request: Request):
    return await connt.reg(request)


@app.post('/login')
async def auth(request: Request):
    return await connt.auth(request)


@app.post('/execute')
async def execute(request: Request):
    return await connt.mult_execute(request)


# if __name__ == "__main__":
#     uvicorn.run(app, host=config['HOST'], port=int(config['PORT']))
