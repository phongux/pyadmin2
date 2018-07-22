from beaker.middleware import SessionMiddleware
import importlib, json


def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    params = request.params
    post = request.POST
    res = Response()
    import pyadmin.login
    importlib.reload(pyadmin.login)
    # Get the session object from the environ
    session = environment['beaker.session']

    # Check to see if a value is in the session
    # user = 'username' in session

    if not 'username' in session:
        page = pyadmin.login.loginform
        response = Response(body=page,
                            content_type="text/html",
                            charset="utf8",
                            status="200 OK")

    elif not 'password' in session:
        page = pyadmin.login.loginform
        response = Response(body=page,
                            content_type="text/html",
                            charset="utf8",
                            status="200 OK")
    else:
        user = session['username']
        passwd = session['password']

        import psycopg2, pyadmin.conn, hashlib, datetime
        importlib.reload(pyadmin.conn)

        try:
            con = psycopg2.connect(pyadmin.conn.conn)
        except:
            page = "Can not access databases"

        cur = con.cursor()
        cur.execute(
            "select username,account_password,account_level from account where username=%s and account_password=%s ",
            (user, passwd,))
        ps = cur.fetchall()
        if len(ps) == 0:
            page = pyadmin.login.login_again
            response = Response(body=page,
                                content_type="text/html",
                                charset="utf8",
                                status="200 OK")

        else:
            if ps[0][2] == 2:
                if not 'cols[]' in post:
                    cols = []
                else:
                    cols = post.getall('cols[]')
                inscols = [col for col in cols if col not in ['id', 'update_time']]
                types = {}

                if not 'table' in post:
                    page = pyadmin.login.login_again
                    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
                else:
                    table = post['table']
                    cur.execute(
                        "select column_name, data_type from information_schema.columns where table_name = '" + table + "'")
                    rows = cur.fetchall()
                    for row in rows:
                        types[row[0]] = row[1]

                    # cur.execute("select * from %s limit 1"%table)
                    # cols = [desc[0] for desc in cur.description]

                    # cols = [desc[0] for desc in rows]

                    page = ""
                    errors = ""
                    if 'delete[]' in post:
                        for row in list(post.getall('delete[]')):
                            if row != '':
                                cur.execute("delete from " + table + " where id = %s""", (int(row),))
                    if 'lenupdate' in post:
                        if int(post['lenupdate']) > 0:
                            for i in range(int(post['lenupdate'])):
                                if post['update[%s][column]' % i] == 'account_password':
                                    cur.execute("update " + table + " set " + post[
                                        'update[%s][column]' % i] + """ = NULLIF(%s,''), update_time = %s where id = %s """,
                                                (hashlib.sha512(
                                                    post['update[%s][value]' % i].encode('utf-8')).hexdigest(),
                                                 datetime.datetime.today(), post['update[%s][id]' % i]))

                                # try:
                                #	cur.execute("update " + table + " set "+ post['update[%s][column]'%i] +""" = NULLIF(%s,''), update_time = %s where id = %s """,(hashlib.sha512(post['update[%s][value]'%i].encode('utf-8')).hexdigest(), datetime.datetime.today(), post['update[%s][id]'%i]))
                                # except psycopg2.Error as e:
                                #	errors += " save errors"  + e.diag.message_primary
                                #		pass
                                else:
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
                                                    (json.dumps(post['update[%s][value]' % i]),
                                                     datetime.datetime.today(), post['update[%s][id]' % i]))

                                    else:
                                        cur.execute("update " + table + " set " + post[
                                            'update[%s][column]' % i] + """ = NULLIF(%s,''), update_time = %s  where id = %s """,
                                                    (post['update[%s][value]' % i], datetime.datetime.today(),
                                                     post['update[%s][id]' % i]))

                                    # try:
                                    #	cur.execute("update " + table + " set "+ post['update[%s][column]'%i] +""" = NULLIF(%s,''), update_time = %s  where id = %s """,(post['update[%s][value]'%i], datetime.datetime.today(),post['update[%s][id]'%i]))
                                    # except psycopg2.Error as e:
                                    #		errors += " save errors"  + e.diag.message_primary
                                    #		pass

                    if 'leninsert' in post:
                        if int(post['leninsert']) > 0:
                            for i in range(int(post['leninsert'])):
                                values = ()
                                for colname in inscols:
                                    if colname == 'account_password':
                                        values += ("NULLIF('" + hashlib.sha512(
                                            post['insert[%s][%s]' % (i, colname)].encode(
                                                'utf-8')).hexdigest() + "','')",)
                                    elif types[colname] == 'integer':
                                        values += ("NULLIF('" + post['insert[%s][%s]' % (i, colname)].replace("'",
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

                                cur.execute("""insert into """ + table + """ (""" + ",".join(
                                    inscols) + """) values ( """ + ",".join(values) + """)""")
                            # try:
                            #	cur.execute("""insert into """ + table + """ (""" + ",".join(inscols) + """) values ( """+ ",".join(values) + """)""")
                            # except psycopg2.Error as e:
                            # con.rollback()
                            # errors += " save errors"# + e.diag.message_primary
                            # pass

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
        con.commit()
        cur.close()
        con.close()

    return response(environment, start_response)


import pyadmin.sess

importlib.reload(pyadmin.sess)
session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
