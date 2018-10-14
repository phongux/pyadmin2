from beaker.middleware import SessionMiddleware
import importlib
import json
import requests
import psycopg2
import psycopg2.extras
import psycopg2.extensions
import hashlib
import pyadmin.conn
import pyadmin.sess

importlib.reload(pyadmin.sess)
importlib.reload(pyadmin.conn)
from pyadmin.conn import conn


def update_captra(captra, user, passwd):
    conn = psycopg2.connect(pyadmin.conn.conn)
    cur = conn.cursor()
    cur.execute("update account set captra=%s where username=%s and account_password=%s", (captra, user, passwd))
    conn.commit()
    cur.close()
    conn.close()


def get_account(user, passwd):
    con = psycopg2.connect(conn)
    cur = con.cursor()
    cur.execute(
        "select username,account_password,account_level,gender,company,depart,birthday from account where username=%s and account_password=%s ",
        (user, hashlib.sha512(passwd.encode('utf-8')).hexdigest(),))
    ps = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return ps


def application(environ, start_response):
    from webob import Request, Response
    from datetime import datetime
    request = Request(environ)
    post = request.POST
    import pyadmin.login
    importlib.reload(pyadmin.login)
    # Get the session object from the environ
    session = environ['beaker.session']
    # Check to see if a value is in the session
    # user = 'username' in session
    # passwd = 'password' in session
    api_url = 'https://www.google.com/recaptcha/api/siteverify'
    site_key = '6LdQQmQUAAAAAIX6RkWjiN7AaswBrFw73HMlMAw4'
    secret_key = '6LdQQmQUAAAAAGhiipTy057aMWHnPuLkEQet8pDy'
    # Set some other session variable

    r = requests.get(
        f"{api_url}?secret={secret_key}&response={post['g-recaptcha-response']}&remoteip={environ['HTTP_HOST']}")
    res = json.loads(r.text)

    if not 'username' in post or post['username'] == '' or not 'password' in post \
            or post['password'] == '' or res['success'] == False:
        page = f"{pyadmin.login.loginform}"
    else:
        user = post['username']
        passwd = post['password']
        if res['success'] == True:
            ps = get_account(user, passwd)
            if len(ps) == 0:
                page = f"{pyadmin.login.login_form}"
            else:
                session['username'] = user
                session['password'] = hashlib.sha512(passwd.encode('utf-8')).hexdigest()
                session['gender'] = ps[0][3]
                session['company'] = ps[0][4]
                session['depart'] = ps[0][5]
                session['birthday'] = ps[0][6]
                session['captra'] = post['g-recaptcha-response']
                update_captra(post['g-recaptcha-response'], user, hashlib.sha512(passwd.encode('utf-8')).hexdigest())
                session.save()
                page = f"""
                    <!doctype html>
                    <html>
                            <head>
                                <meta http-equiv="refresh" content="0; url=/wsgi/pyadmin/index"/>
                                <title> redirect login </title>
                            </head>	
                        <body>
                        </body>
                    </html>"""
        else:
            page = f"{pyadmin.login.loginform}"

    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")

    return response(environ, start_response)


# Configure the SessionMiddleware

session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
