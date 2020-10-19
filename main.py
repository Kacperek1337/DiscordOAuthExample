import json
import os

import uvicorn
from fastapi import Cookie, FastAPI, Response
from rauth import OAuth2Service
from starlette.responses import RedirectResponse

app = FastAPI()

HOST = '127.0.0.1'
PORT = 8000


redirect_uri = f'http://{HOST}:{PORT}/discord'
discord = OAuth2Service(
    name='discord',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    base_url='https://discord.com/api/'
)
authorize_url = discord.get_authorize_url(
        scope='identify',
        response_type='code',
        redirect_uri=redirect_uri
)


@app.get('/me')
async def me(token: str = Cookie(None)):
    session = discord.get_session(token)
    return session.get('users/@me').json()


@app.get('/login')
async def login():
    return RedirectResponse(authorize_url)


@app.get('/discord')
async def discord_callback(response: Response, code: str):
    response.set_cookie(
        key='token',
        value=discord.get_access_token(
            data={
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            },
            decoder=json.loads
        )
    )
    return 'Signed in!'


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT)
