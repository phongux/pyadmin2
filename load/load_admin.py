from beaker.middleware import SessionMiddleware
import importlib


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
        response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    elif not 'password' in session:
        page = pyadmin.login.loginform
        response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    else:
        user = session['username']
        passwd = session['password']

        import psycopg2, pyadmin.conn
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
            response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
        else:
            if ps[0][2] == 2:
                if not 'display' in post:
                    display = 200
                else:
                    display = int(post['display'])
                if not 'page' in post:
                    page = 1
                else:
                    page = post['page']

                if not 'table' in post:
                    table = ''
                else:
                    table = post['table']

                if not 'cols[]' in post:
                    cols = []
                    query_cols = "*"
                else:
                    cols = post.getall('cols[]')
                    query_cols = ",".join(post.getall('cols[]'))

                if not 'filcols[]' in post:
                    filcols = []
                else:
                    filcols = post.getall('filcols[]')

                if not 'orderby[]' in post:
                    orderby = ['id']
                else:
                    orderby = post.getall('orderby[]')

                if not 'by' in post:
                    by = 'asc'
                else:
                    by = post['by']
                # post['types[id]']
                query = []
                for c in cols:
                    if post['types[%s]' % c] == 'int':
                        if 'mor%s' % c in post:
                            if post['mor%s' % c] != "":
                                query.append(c + " > " + post['mor%s' % c] + " ")
                        if 'les%s' % c in post:
                            if post['les%s' % c] != "":
                                query.append(c + " < " + post['les%s' % c] + " ")

                    elif post['types[%s]' % c] == 'datetime' or post['types[%s]' % c] == 'date':
                        if 'mor%s' % c in post:
                            if post['mor%s' % c] != "":
                                query.append(c + " > '" + post['mor%s' % c] + "' ")
                        if 'les%s' % c in post:
                            if post['les%s' % c] != "":
                                query.append(c + " < '" + post['les%s' % c] + "' ")

                    else:
                        if 'fil%s' % c in post:
                            if post['fil%s' % c] != "":
                                query.append(c + " ilike '%" + post['fil%s' % c] + "%' ")

                        if 'notfil%s' % c in post:
                            if post['notfil%s' % c] != "":
                                query.append(c + " not ilike '%" + post['notfil%s' % c] + "%' ")

                        if '%snull' % c in post:
                            if post['%snull' % c] != "":
                                query.append(c + " is " + post['%snull' % c].replace("_", " ") + " ")

                if 'movecols[]' in post:
                    if len(post.getall('movecols[]')) != 0:
                        query_cols = ",".join(post.getall('movecols[]'))
                    else:
                        query_cols = "*"
                else:
                    query_cols = "*"

                start = (int(page) - 1) * display
                if 'que' in post:
                    if post['que'] == '':
                        que = ''
                    else:
                        que = post['que'].replace("\\", " ")

                else:
                    que = 'select '

                if 'table' in post:
                    if post['table'] != '':
                        if post['table'] == 'create_table':
                            cur.execute("select *from (select 'create successful' as status) as success")
                            rows_count = 1
                            rows = cur.fetchall()

                        if len(query) > 0:
                            # try:
                            cur.execute(
                                """select count(*) from (""" + que + """) as jotikaandmendaka where """ + """ and """.join(
                                    query))
                            rows_count = cur.fetchone()

                            cur.execute(
                                """select * from (""" + que + """) as jotikaandmendaka where """ + """ and """.join(
                                    query) + """ order by """ + """,""".join(
                                    orderby) + """ """ + by + """ limit %s offset %s """ % (display, start))
                            rows = cur.fetchall()
                        # except:
                        #	rows_count=[0]
                        #	rows = []
                        # a = """select * from ("""  + que + """) as jotikaandmendaka where """ + """ and """.join(query) + """ order by """ + """,""".join(orderby) +""" """ + by + """ limit %s offset %s """%(display,start)
                        else:

                            # try:
                            cur.execute("""select count(*) from (""" + que + """) as jotikaandmendaka  """)
                            rows_count = cur.fetchone()
                            cur.execute(
                                """select * from (""" + que + """) as jotikaandmendaka  order by """ + """,""".join(
                                    orderby) + """ """ + by + """ limit %s offset %s """ % (display, start))
                            rows = cur.fetchall()
                        # a ="""select * from ("""  + que + """) as jotikaandmendaka  order by """ + """,""".join(orderby) +""" """ + by + """ limit %s offset %s """%(display,start)
                        # except:
                        #	rows_count=[0]
                        #	rows = []

                        sum_page = (int(rows_count[0]) / display) + 1

                        row = []
                        for ro in rows:
                            row.append(list(ro))
                        page = '{"product":'
                        objects_list = []
                        import json, collections

                        for i in range(len(row)):
                            d = collections.OrderedDict()
                            d['idha'] = i + 1  # row[0]
                            for j in range(len(cols)):
                                if type(row[i][j]).__name__ == 'datetime' or type(row[i][j]).__name__ == 'date':
                                    d[cols[j]] = str(row[i][j])
                                elif type(row[i][j]).__name__ == 'float':
                                    d[cols[j]] = str(round(row[i][j], 9))
                                elif type(row[i][j]).__name__ == 'Decimal':
                                    d[cols[j]] = str(row[i][j])
                                elif type(row[i][j]).__name__ == 'dict' or type(row[i][j]).__name__ == 'list':
                                    d[cols[j]] = json.dumps(row[i][j], ensure_ascii=False).encode('utf8').decode(
                                        'utf-8')
                                else:
                                    d[cols[j]] = row[i][j]
                            objects_list.append(d)

                        # print(objects_list)
                        page += json.dumps(objects_list)
                        page += ""","sum_page":%s}""" % (int(sum_page))

                    else:
                        page = ""

                else:
                    page = ""

                # cur.execute("""select count(*) from """ + table + " where " +  " ".join(query) +   " id > 0")
                # rows_count = cur.fetchone()
                # a ="select "+ query_cols +" from " + table + " where " + " ".join(query) + " id > 0 order by " + ",".join(orderby) +" " + by + " limit %s offset %s "%(display,start)
                # cur.execute("select "+ query_cols +" from " + table + " where " + " ".join(query) + " id > 0 order by " + ",".join(orderby) +" " + by + " limit %s offset %s "%(display,start))
                # rows = cur.fetchall()
                # column_names = [desc[0] for desc in cur.description if desc[0] not in hidecols]
                # data_types = [type(val).__name__ for index,val in enumerate(rows[0])]




                # page +=""","sum_page":%s ,"columns":"""%(int(sum_page))
                # objects_columns =[]
                # for column in column_names:
                #	c = collections.OrderedDict()
                #	c["column"] = column
                #	objects_columns.append(c)
                # columns = json.dumps(objects_columns)
                # page += str(columns)



                response = Response(body=page,
                                    content_type="application/json",
                                    charset="utf8",
                                    status="200 OK")
            else:
                page = pyadmin.login.login_again
                response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
            con.commit()
            cur.close()
            con.close()
    return response(environment, start_response)


import pyadmin.sess

importlib.reload(pyadmin.sess)
session_opts = pyadmin.sess.session_opts

application = SessionMiddleware(application, session_opts)
