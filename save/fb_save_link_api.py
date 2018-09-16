def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    params = request.params
    post = request.POST
    res = Response()
    import psycopg2
    import pyadmin.conn
    import importlib
    importlib.reload(pyadmin.conn)
    link = post['link']
    con = psycopg2.connect(pyadmin.conn.conn)
    cur = con.cursor()
    cur.execute("""create table if not exists fb_account
	(id serial8 primary key,
	link text unique,
	note text,
	created_time timestamp default now(),
	update_time timestamp default now())""")
    con.commit()
    cur.close()
    con.close()

    con = psycopg2.connect(pyadmin.conn.conn)
    cur = con.cursor()
    cur.execute(
        "insert into fb_account(link) values(%s) on conflict (link) do nothing ",
        (link,))
    con.commit()
    cur.close()
    con.close()
    page = f"{{result:'{link}'}}"
    response = Response(body=page,
                        content_type="application/json",
                        charset="utf8",
                        status="200 OK")
    return response(environment, start_response)
