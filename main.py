'''
Starts a Twitter clone web app.
'''
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from markupsafe import escape
from markdown_compiler import compile_lines
import uvicorn
import sqlite3
import re

app = FastAPI()
templates = Jinja2Templates(directory='templates')

app.mount("/static", StaticFiles(directory="static"), name="static")

# check_credentials needs a request passed in everywhere 
# checks if there is a valid logged in user attached to the request
def check_credentials(request: Request): 
    '''
    returns username if user is logged in 
    if not logged in return None
    '''
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    
    if username is None or password is None:
        print('not logged in')
        return False

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT username FROM users
    WHERE username = ? AND password = ?;
    """

    cur.execute(sql, [username, password])
    row = cur.fetchone()

    con.close()

    if row:
        print(f'logged in as {username}')
        return row[0]
    else: 
        print('not logged in')
        return False

# retrieves all data info from database
# and passes it into html templates
@app.get('/', response_class=HTMLResponse)
async def index(request: Request):

    # display success message after user deletes account
    success_message = request.query_params.get('deleted_user_message')

    page = int(request.query_params.get('page', 0))
    offset = page * 50

    # extract username from database
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT messages.id, users.username, users.age, messages.message, messages.created_at, messages.edited_at
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC, messages.id DESC
    LIMIT 50 OFFSET ?;
    """

    cur.execute(sql, [offset])

    messages = []
    for row in cur.fetchall():
        message_text = compile_lines(str(escape(row[3])))

        message_text = re.sub(
            r'(https?://[^\s<>"]+)',
            r'<a href="\1">\1</a>',
            message_text
        )

        message_dict = {
            'id': row[0],
            'username': row[1],
            'age': row[2],
            'message': message_text,
            'created_at': row[4],
            'edited_at': row[5],
        }
        messages.append(message_dict)

    con.close()

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
            'messages': messages,
            'deleted_user_message': success_message,
            'page': page,
        }
    )

@app.get('/messages.json')
async def messages_json(request: Request):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    sql = """
    SELECT messages.id, users.username, users.age, messages.message,
           messages.created_at, messages.edited_at
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC, messages.id DESC;
    """

    cur.execute(sql)

    messages = []
    for row in cur.fetchall():
        message_dict = {
            'id': row[0],
            'username': row[1],
            'age': row[2],
            'message': row[3],
            'created_at': row[4],
            'edited_at': row[5],
        }
        messages.append(message_dict)

    con.close()

    return messages

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    query_username = request.query_params.get('username')
    query_password = request.query_params.get('password')

    error = None

    # only check database if there is an input
    if query_username is not None or query_password is not None:
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()

        sql = """
        SELECT username FROM users
        WHERE username = ? AND password = ?;
        """

        cur.execute(sql, [query_username, query_password])
        row = cur.fetchone()

        con.close()

        # if there is input, store this new username and password in cookies
        if row: 
            response = RedirectResponse(url='/', status_code=302)
            response.set_cookie(key='username', value=query_username)
            response.set_cookie(key='password', value=query_password)
            return response
        else:
            error = 'Incorrect username or password.'

    response = templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
            'error': error,
        }
    )
    return response

@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    response = templates.TemplateResponse(
        request=request,
        name='logout.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
        }
    )
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/create_message', response_class=HTMLResponse)
async def create_message(request: Request):
    username = check_credentials(request)

    if not username:
        return RedirectResponse(url='/login', status_code=302)
    
    query_message = request.query_params.get('message')
    error = None

    if query_message is not None:
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()

        sql = """
        SELECT id FROM users
        WHERE username = ?;
        """

        cur.execute(sql, [username])
        row = cur.fetchone()

        user_id = row[0]

        sql = """
        INSERT INTO messages (sender_id, message)
        VALUES (?, ?);
        """

        cur.execute(sql, [user_id, query_message])
        con.commit()
        con.close()

        return RedirectResponse(url='/', status_code=302)

    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={
            'is_logged_in': username,
            'username': username,
            'error': error,
        }
    )

@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    query_username = request.query_params.get('username')
    query_password1 = request.query_params.get('password1')
    query_password2 = request.query_params.get('password2')
    query_age = request.query_params.get('age')

    error = None

    if any([query_username, query_password1, query_password2, query_age]):
        if (
            not query_username or not query_username.strip()
            or not query_password1 or not query_password1.strip()
            or not query_password2 or not query_password2.strip()
            or not query_age or not query_age.strip()
        ):
            error = 'Missing information.'
        elif query_password1 != query_password2:
            error = 'Passwords do not match.'
        else:
            con = sqlite3.connect('twitter_clone.db')
            cur = con.cursor()

            sql = """
            INSERT INTO users (username, password, age)
            VALUES (?, ?, ?);
            """

            try:
                cur.execute(sql, [query_username, query_password1, query_age])
                con.commit()

                response = RedirectResponse(url='/', status_code=302)
                response.set_cookie(key='username', value=query_username)
                response.set_cookie(key='password', value=query_password1)
                con.close()
                return response

            except sqlite3.IntegrityError:
                error = 'That username already exists.'
                con.close()

    return templates.TemplateResponse(
        request=request,
        name='create_user.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
            'error': error,
        }
    )

@app.get('/delete_message')
async def delete_message(request: Request):
    username = check_credentials(request)

    if not username: 
        return RedirectResponse(url='/login', status_code=302)

    message_id = request.query_params.get('message_id')

    if message_id is not None:
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()

        sql = """
        DELETE FROM messages
        WHERE id = ?;
        """
        cur.execute(sql, [message_id])
        con.commit()
        con.close()

    return RedirectResponse(url='/', status_code=302)

@app.get('/edit_message', response_class=HTMLResponse)
async def edit_message(request: Request):
    username = check_credentials(request)

    if not username:
        return RedirectResponse(url='/login', status_code=302)

    message_id = request.query_params.get('message_id')
    new_message = request.query_params.get('message')

    if message_id is None:
        return RedirectResponse(url='/', status_code=302)

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # update database row
    if new_message is not None:
        sql = """
        UPDATE messages
        SET message = ?, edited_at = current_timestamp
        WHERE id = ?;
        """
        cur.execute(sql, [new_message, message_id])
        con.commit()
        con.close()

        return RedirectResponse(url='/', status_code=302)

    # rerun sql query to get updated row from database
    sql = """
    SELECT message FROM messages
    WHERE id = ?;
    """
    cur.execute(sql, [message_id])
    row = cur.fetchone()
    con.close()

    if row is None:
        return RedirectResponse(url='/', status_code=302)

    return templates.TemplateResponse(
        request=request,
        name='edit_message.html',
        context={
            'is_logged_in': username,
            'username': username,
            'message_id': message_id,
            'message': row[0],
            'error': None,
        }
    )

@app.get('/search', response_class=HTMLResponse)
async def search(request: Request):
    query = request.query_params.get('query')
    messages = []

    if query:
        con = sqlite3.connect('twitter_clone.db')
        cur = con.cursor()

        sql = """
        SELECT messages.id, users.username, users.age, messages.message,
               messages.created_at, messages.edited_at
        FROM messages
        JOIN users ON messages.sender_id = users.id
        WHERE messages.message LIKE ?
        ORDER BY messages.created_at DESC, messages.id DESC
        LIMIT 50;
        """

        cur.execute(sql, [f'%{query}%'])

        for row in cur.fetchall():
            message_text = compile_lines(str(escape(row[3])))
            message_text = re.sub(
                r'(https?://[^\s<>"]+)',
                r'<a href="\1">\1</a>',
                message_text
            )
            messages.append({
                'id': row[0],
                'username': row[1],
                'age': row[2],
                'message': message_text,
                'created_at': row[4],
                'edited_at': row[5],
            })

        con.close()

    return templates.TemplateResponse(
        request=request,
        name='search.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
            'messages': messages,
            'query': query,
        }
    )

@app.get('/delete_user')
async def delete_user(request: Request):
    username = check_credentials(request)

    if not username:
        return RedirectResponse(url='/login', status_code=302)

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()

    # get logged-in user's id
    sql = """
    SELECT id FROM users
    WHERE username = ?;
    """
    cur.execute(sql, [username])
    row = cur.fetchone()

    if row is not None:
        user_id = row[0]

        # delete that user's messages first
        sql = """
        DELETE FROM messages
        WHERE sender_id = ?;
        """
        cur.execute(sql, [user_id])

        # delete the user account
        sql = """
        DELETE FROM users
        WHERE id = ?;
        """
        cur.execute(sql, [user_id])

        con.commit()

    con.close()

    response = RedirectResponse(
        url='/?deleted_user_message=Account successfully deleted.',
        status_code=302
    )
    response.delete_cookie(key='username')
    response.delete_cookie(key='password')
    return response

@app.get('/change_password', response_class=HTMLResponse)
async def change_password(request: Request):
    username = check_credentials(request)

    if not username:
        return RedirectResponse(url='/login', status_code=302)

    old_password = request.query_params.get('old_password')
    new_password1 = request.query_params.get('new_password1')
    new_password2 = request.query_params.get('new_password2')

    error = None
    success = None

    # checks if user has submitted form
    if old_password is not None or new_password1 is not None or new_password2 is not None:
        # checks if anything was left blank in submission
        if not old_password or not new_password1 or not new_password2:
            error = 'Missing information.'

        elif new_password1 != new_password2:
            error = 'New passwords do not match.'

        else:
            con = sqlite3.connect('twitter_clone.db')
            cur = con.cursor()

            sql = """
            SELECT id FROM users
            WHERE username = ? AND password = ?;
            """
            cur.execute(sql, [username, old_password])
            row = cur.fetchone()

            if row is None:
                error = 'Old password is incorrect.'
                con.close()

            else:
                user_id = row[0]

                sql = """
                UPDATE users
                SET password = ?
                WHERE id = ?;
                """
                cur.execute(sql, [new_password1, user_id])
                con.commit()
                con.close()

                response = RedirectResponse(url='/', status_code=302)
                response.set_cookie(key='username', value=username)
                response.set_cookie(key='password', value=new_password1)
                return response

    return templates.TemplateResponse(
        request=request,
        name='change_password.html',
        context={
            'is_logged_in': username,
            'username': username,
            'error': error,
            'success': success,
        }
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

