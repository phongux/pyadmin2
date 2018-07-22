from beaker.middleware import SessionMiddleware
import importlib
import json,requests
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
    user = 'username' in session
    passwd = 'password' in session
    api_url = 'https://www.google.com/recaptcha/api/siteverify'
    site_key = '6LdQQmQUAAAAAIX6RkWjiN7AaswBrFw73HMlMAw4'
    secret_key = '6LdQQmQUAAAAAGhiipTy057aMWHnPuLkEQet8pDy'
    # Set some other session variable
    # session['user_id'] = 10
    # user_id = 'user_id' in session
    r = requests.get(f"{api_url}?secret={secret_key}&response={post['g-recaptcha-response']}&remoteip={environ['HTTP_HOST']}")
    res = json.loads(r.text)

    if not 'username' in post or post['username'] == '' or not 'password' in post\
    or post['password'] == '' or res['success']==False:
        page = f"{pyadmin.login.loginform}"
    else:
        user = post['username']
        passwd = post['password']
        if res['success'] == True:
            import psycopg2, psycopg2.extras, psycopg2.extensions, hashlib, pyadmin.conn
            importlib.reload(pyadmin.conn)
            from pyadmin.conn import conn
            try:
                con = psycopg2.connect(conn)
            except:
                page = "Can not access databases"

            cur = con.cursor()
            cur.execute(
                "select username,account_password,account_level from account where username=%s and account_password=%s ",
                (user, hashlib.sha512(passwd.encode('utf-8')).hexdigest(),))
            ps = cur.fetchall()
            if len(ps) == 0:
                page = f"{pyadmin.login.login_form}"
            else:
                session['username'] = user
                session['password'] = hashlib.sha512(passwd.encode('utf-8')).hexdigest()
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
        con.commit()
        cur.close()
        con.close()
    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")

    return response(environ, start_response)

# Configure the SessionMiddleware
import pyadmin.sess
importlib.reload(pyadmin.sess)
session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
