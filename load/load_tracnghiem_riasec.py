from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from beaker.middleware import SessionMiddleware
import importlib
import psycopg2
import pyadmin.conn
import json
import collections
import pyadmin.sess
import logging

logging.basicConfig(level=logging.ERROR)
importlib.reload(pyadmin.conn)
importlib.reload(pyadmin.sess)


def get_conection():
    connection = psycopg2.connect(pyadmin.conn.conn)
    return connection


def convert_row(i, row):
    d = collections.OrderedDict()
    d['idha'] = i + 1  # row[0]
    for j in range(len(o)):
        d[cols[j]] = row[i][j]
    return d


def get_account(user, passwd, captra):
    con = get_conection()
    cur = con.cursor()
    cur.execute(
        "select username,account_password,account_level from account where username=%s and account_password=%s and captra=%s ",
        (user, passwd, captra))
    ps = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return ps


def count_rows():
    con = get_conection()
    cur = con.cursor()
    cur.execute(f"""select count(*) from {table} """)
    rows_count = cur.fetchone()
    con.commit()
    cur.close()
    con.close()
    return rows_count


def get_rows(display, start_w):
    con = get_conection()
    cur = con.cursor()
    cur.execute(
        f"""select id,ma_cau_hoi,cau_hoi from trac_nghiem_riasec order by id limit {display} offset {start_w} """)
    rows = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return rows


def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    # params = request.params
    post = request.POST
    # res = Response()
    import pyadmin.login
    importlib.reload(pyadmin.login)
    session = environment['beaker.session']

    if 'username' not in session:
        page = pyadmin.login.loginform
    elif 'password' not in session:
        page = pyadmin.login.loginform
    else:
        user = session['username']
        passwd = session['password']
        captra = session['captra']
        ps = get_account(user, passwd, captra)
        if ps[0][2] > 0:
            if 'display' not in post:
                display = 200
            else:
                display = int(post['display'])
            if 'page' not in post:
                page = 1
            else:
                page = post['page']
            start_w = (int(page) - 1) * display
            rows_count = count_rows()
            rows = get_rows(display, start_w)
            sum_page = (int(rows_count[0]) / display) + 1
            row = []
            for ro in rows:
                row.append(list(ro))
            page = '{"product":'
            objects_list = []
            with ThreadPoolExecutor(max_workers=1) as executor:
                # Start the load operations and mark each future with its URL
                futures = [executor.submit(convert_row, i, row) for i in range(len(row))]
                for future in as_completed(futures):
                    try:
                        objects_list.append(future.result())
                    except Exception as exc:
                        logging.error(exc)
                    else:
                        pass
            page += json.dumps(objects_list)
            page += ""","sum_page":%s}""" % (int(sum_page))
        else:
            page = pyadmin.login.login_again
    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    return response(environment, start_response)


session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
