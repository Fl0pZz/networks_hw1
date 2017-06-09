import hashlib

import binascii
import os

import bottle
from bottle import run, route, template, post, request, HTTPResponse, static_file

DB = {}


def password(string, hash):
    salt = b'a'
    if hash == 'sha256':
        tmp = hashlib.sha256(bytes(string, 'utf-8'))
        for i in range(10000):
            tmp = hashlib.sha256(tmp.digest())
        tmp = hashlib.sha256(tmp.digest() + salt)
        return "sha256${}${}${}".format(10000, salt, tmp.hexdigest())
    else:
        tmp = hashlib.pbkdf2_hmac('sha256', bytes(string, 'utf-8'), salt, 10000)
        return "pbkdf2${}${}${}".format(10000, salt, binascii.hexlify(tmp).decode('utf-8'))


@post("/login")
@route('/login')
def login():
    if request.method == "GET":
        a = """<!DOCTYPE html>
            <html>
            <body>
            <form action='/login' method='post'>
                <input type="text" name="username">
                <input type="password" name="pass">
                <input type="submit" value="login">
            </form>
            </body>
            </html>"""
        return template(a)
    else:
        global DB
        username = request.forms.get("username")
        passw = request.forms.get("pass")
        passo = str(DB.get(username, b'pbkdf2$10000$a$a'))

        cipher, num_of_iterations, salt, hash = passo.split('$')
        a = password(passw, cipher)
        if passo == a:
            pass
        response = HTTPResponse(status=200)
        response.set_cookie('sessionid', 'sessionid')
        return response


@route('/logout')
def logout():
    response = HTTPResponse(status=200)
    response.delete_cookie('sessionid')
    return response


@post("/registration")
@route('/registration')
def register():
    if request.method == "GET":
        a = """<!DOCTYPE html>
        <html>
        <body>
        <form action='/registration' method='post'>
            <input type="text" name="username">
            <input type="password" name="pass">
            <input type="submit" value="register">
        </form>
        </body>
        </html>"""
        return template(a)
    else:
        global DB
        username = request.forms.get("username")
        passw = request.forms.get("pass")
        passo = password(passw, 'pbkdf2')
        DB[username] = passo
        return HTTPResponse(status=200)

def a():
    pass

@post("/db")
@route('/db')
def db():
    from bottle import request
    if request.method == "GET":
        a = """<!DOCTYPE html>
        <html>
        <body>
        <form action='/db' method='post'>
            <input type="text" name="request">
            <input type="submit" value="commit">
        </form>
        </body>
        </html>"""
        return template(a)
    else:
        global DB
        request = request.forms.get("request")
        DB['abc'] = request
        return HTTPResponse(status=200)


@route('/calc')
def calc():
    a = 5000
    b = []
    for i in range(a):
        if a % (i + 1) == 0:
            b.append(str(i))
    return HTTPResponse(status=200)


@route('/ping')
def ping():
    os.system("ping -c 5 " + request.get_header('X-Forwarded-For'))
    return HTTPResponse(status=200)


@route('/file/<filename:path>')
def file(filename):
    return static_file(filename, root='/vagrant/server/static/files', download=filename)


if __name__ == "__main__":
    run(host='0.0.0.0', port=8080)
else:
    app = application = bottle.default_app()
