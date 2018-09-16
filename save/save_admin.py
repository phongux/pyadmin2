from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from beaker.middleware import SessionMiddleware
import json
import psycopg2
import pyadmin.conn
import hashlib
import datetime
import importlib
import pyadmin.login
import pyadmin.sess

importlib.reload(pyadmin.sess)
importlib.reload(pyadmin.login)
importlib.reload(pyadmin.conn)


def get_connection():
    connection = psycopg2.connect(pyadmin.conn.conn)
    return connection


def delete_row(table, rowid):
    con = get_connection()
    cur = con.cursor()
    cur.execute(f"delete from {table} where id = %s""", (int(rowid),))
    con.commit()
    cur.close()
    con.close()


def update_row(i, table, post, types):
    if post['update[%s][column]' % i] == 'account_password':
        con = get_connection()
        cur = con.cursor()
        cur.execute("update " + table + " set " + post[
            'update[%s][column]' % i] + """ = NULLIF(%s,''), update_time = %s where id = %s """,
                    (hashlib.sha512(
                        post['update[%s][value]' % i].encode('utf-8')).hexdigest(),
                     datetime.datetime.today(), post['update[%s][id]' % i]))
        con.commit()
        cur.close()
        con.close()

    else:
        con = get_connection()
        cur = con.cursor()
        if types[post['update[%s][column]' % i]] == 'integer':
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,'')::int, update_time = %s  where id = %s """,
                        (post['update[%s][value]' % i], datetime.datetime.today(),
                         post['update[%s][id]' % i]))
        elif types[post['update[%s][column]' % i]] == 'bigint':
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,'')::bigint, update_time = %s  where id = %s """,
                        (post['update[%s][value]' % i], datetime.datetime.today(),
                         post['update[%s][id]' % i]))
        elif types[post['update[%s][column]' % i]] == 'numeric':
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,'')::numeric, update_time = %s  where id = %s """,
                        (post['update[%s][value]' % i], datetime.datetime.today(),
                         post['update[%s][id]' % i]))
        elif types[post['update[%s][column]' % i]] == 'json':
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,'')::json, update_time = %s  where id = %s """,
                        (json.dumps(post['update[%s][value]' % i]),
                         datetime.datetime.today(), post['update[%s][id]' % i]))
        elif types[post['update[%s][column]' % i]] == 'timestamp without time zone':
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,'')::timestamp, update_time = %s  where id = %s """,
                        (post['update[%s][value]' % i],
                         datetime.datetime.today(), post['update[%s][id]' % i]))

        else:
            cur.execute("update " + table + " set " + post[
                'update[%s][column]' % i] + """ = NULLIF(%s,''), update_time = %s  where id = %s """,
                        (post['update[%s][value]' % i], datetime.datetime.today(),
                         post['update[%s][id]' % i]))
        con.commit()
        cur.close()
        con.close()


def insert_row(i, table, post, types, inscols):
    values = ()
    for colname in inscols:
        if colname == 'account_password':
            values += ("NULLIF('" + hashlib.sha512(
                post['insert[%s][%s]' % (i, colname)].encode(
                    'utf-8')).hexdigest() + "','')",)
        elif types[colname] == 'integer':
            values += (
                "NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
                                                                           "''") + "','')::integer",)
        elif types[colname] == 'bigint':
            values += ("NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
                                                                                  "''") + "','')::biginteger",)
        elif types[colname] == 'numeric':
            values += ("NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
                                                                                  "''") + "','')::numeric",)
        elif types[colname] == 'json':
            values += ("NULLIF('" + json.dumps(
                post['insert[%s][%s]' % (i, colname)].replace("'", "''")) + "','')::json",)
        elif types[colname] == 'timestamp without time zone':
            values += ("NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
                                                                                  "''") + "','')::timestamp",)
        else:
            values += ("NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
                                                                                  "''") + "','')",)

    con = get_connection()
    cur = con.cursor()
    cur.execute("""insert into """ + table + """ (""" + ",".join(
        inscols) + """) values ( """ + ",".join(values) + """)""")
    con.commit()
    cur.close()
    con.close()


def delete_check(post, table):
    if 'delete[]' in post:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(delete_row, table, rowid) for rowid in
                       list(post.getall('delete[]')) if rowid != ''}
            wait(futures)


def update_check(post, table, types):
    if 'lenupdate' in post:
        if int(post['lenupdate']) > 0:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(update_row, i, table, post, types) for i in
                           range(int(post['lenupdate']))}
                wait(futures)


def insert_check(post, table, types, inscols):
    if 'leninsert' in post:
        if int(post['leninsert']) > 0:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(insert_row, i, table, post, types, inscols) for i in
                           range(int(post['leninsert']))}
                wait(futures)


def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    params = request.params
    post = request.POST
    res = Response()
    # Get the session object from the environ
    session = environment['beaker.session']

    # Check to see if a value is in the session
    # user = 'username' in session

    if 'username' not in session:
        page = pyadmin.login.loginform
        response = Response(body=page,
                            content_type="text/html",
                            charset="utf8",
                            status="200 OK")

    elif 'password' not in session:
        page = pyadmin.login.loginform
        response = Response(body=page,
                            content_type="text/html",
                            charset="utf8",
                            status="200 OK")
    else:
        user = session['username']
        passwd = session['password']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "select username,account_password,account_level from account where username=%s and account_password=%s ",
            (user, passwd,))
        ps = cur.fetchall()
        con.commit()
        cur.close()
        con.close()

        if len(ps) == 0:
            page = pyadmin.login.login_again
            response = Response(body=page,
                                content_type="text/html",
                                charset="utf8",
                                status="200 OK")

        else:
            if ps[0][2] == 2:
                if 'cols[]' not in post:
                    cols = []
                else:
                    cols = post.getall('cols[]')
                inscols = [col for col in cols if col not in ['id', 'update_time']]
                types = {}
                if 'table' not in post:
                    page = pyadmin.login.login_again
                    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
                else:
                    con = get_connection()
                    cur = con.cursor()
                    table = post['table']
                    cur.execute(
                        "select column_name, data_type from information_schema.columns where table_name = '" + table + "'")
                    rows = cur.fetchall()
                    con.commit()
                    cur.close()
                    con.close()

                    for row in rows:
                        types[row[0]] = row[1]

                    # cur.execute("select * from %s limit 1"%table)
                    # cols = [desc[0] for desc in cur.description]

                    # cols = [desc[0] for desc in rows]

                    page = ""
                    errors = ""
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        futures = {executor.submit(delete_check, post, table),
                                   executor.submit(update_check, post, table, types),
                                   executor.submit(insert_check, post, table, types, inscols)
                                   }
                        wait(futures)
                    page = """{"result":"ok"}"""
                    response = Response(body=page,
                                        content_type="application/json",
                                        charset="utf8",
                                        status="200 OK")
            else:
                page = pyadmin.login.login_again
                response = Response(body=page,
                                    content_type="text/html",
                                    charset="utf8",
                                    status="200 OK")
    return response(environment, start_response)


session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
