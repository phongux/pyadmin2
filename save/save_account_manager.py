from beaker.middleware import SessionMiddleware
import psycopg2
import pyadmin.conn
import datetime
import importlib
import pyadmin.login
import pyadmin.sess

importlib.reload(pyadmin.sess)
importlib.reload(pyadmin.login)
importlib.reload(pyadmin.conn)
import logging

logging.basicConfig(level=logging.DEBUG)


def get_connection():
    connection = psycopg2.connect(pyadmin.conn.conn)
    return connection


def get_account(user, passwd, captra, id):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "select username,account_password,account_level from account where username=%s and account_password=%s and captra=%s and id=%s ",
        (user, passwd, captra, id))
    ps = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return ps


def update_rows(post, table, user,id):
    if 'lenupdate' in post:
        if int(post['lenupdate']) > 0:
            for i in range(int(post['lenupdate'])):
                if post['update[%s][column]' % i] == 'username' or post['update[%s][column]' % i] == 'captra' or post[
                    'update[%s][column]' % i] == 'id' or post['update[%s][column]' % i] == 'account_level':
                    pass
                else:
                    con = get_connection()
                    cur = con.cursor()
                    if post[f'update[{i}][column]'] == 'birthday':
                        cur.execute(f"""update {table} set {post[
                                            'update[%s][column]' % i]} = NULLIF(%s,'')::date, update_time = %s  where id = %s and username=%s """,
                                    (post['update[%s][value]' % i], datetime.datetime.today(), id, user))
                    else:
                        cur.execute(f"""update {table} set {post[
                                            'update[%s][column]' % i]} = NULLIF(%s,''), update_time = %s  where id = %s and username=%s """,
                                    (post['update[%s][value]' % i], datetime.datetime.today(), id, user))
                    con.commit()
                    cur.close()
                    con.close()


def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    post = request.POST
    session = environment['beaker.session']
    if 'username' not in session or 'password' not in session:
        page = pyadmin.login.loginform
    else:
        user = session['username']
        passwd = session['password']
        captra = session['captra']
        id = session['id']
        table = 'account'
        ps = get_account(user, passwd, captra, id)
        if ps[0][2] > 0:
            update_rows(post, table, user,id)
            page = """{"result":"ok"}"""
        else:
            page = pyadmin.login.login_again
    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")


    return response(environment, start_response)

session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
