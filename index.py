from beaker.middleware import SessionMiddleware
import importlib
import pyadmin.sess


def application(environ, start_response):
    from webob import Request, Response
    # from datetime import datetime
    # request = Request(environ)
    # post = request.POST
    import importlib, pyadmin.login
    importlib.reload(pyadmin.login)
    from pyadmin import login

    # Get the session object from the environ
    session = environ['beaker.session']

    # Check to see if a value is in the session
    user = 'username' in session
    passwd = 'password' in session

    # Set some other session variable
    # session['user_id'] = 10
    # user_id = 'user_id' in session

    if not 'username' in session:
        page = pyadmin.login.loginform
    elif not 'password' in session:
        page = pyadmin.login.loginform
    else:
        user = session['username']
        passwd = session['password']
        captra = session['captra']
        import psycopg2, hashlib, pyadmin.conn
        importlib.reload(pyadmin.conn)
        from pyadmin.conn import conn
        try:
            con = psycopg2.connect(conn)
        except:
            page = "Can not access databases"
        cur = con.cursor()
        cur.execute(
            "select username,account_password,account_level from account where username=%s and account_password=%s and captra=%s ",
            (user, passwd, captra))
        ps = cur.fetchall()
        if len(ps) == 0:
            page = pyadmin.login.login_again
        else:
            import pyadmin.module
            importlib.reload(pyadmin.module)
            from pyadmin.module import head, headlink, menuadmin, menuuser, menuhead, menufoot
            page = ""
            page += head + headlink
            page += "<title>home page</title>"
            page += \
                """
                    </head>
                    <body>
                """
            page += menuhead
            if int(ps[0][2]) == 2:
                page += menuadmin
            else:
                page += menuuser
            page += menufoot
            page += """
            <br />
            <br />
            <br />
            <br />"""
            page += """<p> You are successfully logged in !</p>"""
        con.commit()
        cur.close()
        con.close()
    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")
    return response(environ, start_response)


# Configure the SessionMiddleware
importlib.reload(pyadmin.sess)
session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
