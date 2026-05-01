'''
Starts a hello world observer.
'''
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory='templates')

app.mount("/static", StaticFiles(directory="static"), name="static")

# Internal Server Error: 
# always means a python error inside of the function that corresponds to
# the route or "page" you were connecting to in Firefox
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    is_logged_in = True

    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT users.username, users.age, messages.message, messages.created_at
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC;
    """

    cur.execute(sql)

    messages = []
    for row in cur.fetchall():
        message_dict = {
            'username': row[0],
            'age': row[1],
            'message': row[2],
            'created_at': row[3],
        }
        messages.append(message_dict)

    con.close()

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': is_logged_in,
            'messages': messages,
        }
    )

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    is_logged_in = False
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': is_logged_in,
        }
    )

@app.get('/logout', response_class=HTMLResponse)
async def login(request: Request):
    is_logged_in = False
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': is_logged_in,
        }
    )

@app.get('/create_message', response_class=HTMLResponse)
async def login(request: Request):
    is_logged_in = True
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': is_logged_in,
        }
    )

@app.get('/create_user', response_class=HTMLResponse)
async def login(request: Request):
    is_logged_in = False
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': is_logged_in,
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

