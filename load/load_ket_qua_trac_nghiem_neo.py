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


def convert_row(i, row, cols):
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


def count_rows(user):
    con = get_conection()
    cur = con.cursor()
    cur.execute(f""" select count(*)from (  select ten_nhom,k.thang_do, dien_giai,huong_nghiep from (select case when sum < thap 
   then 'thap'
   when thap < sum and sum < cao 
   then 'trung_binh'
   else 'cao'
   end as thang_do,nhom_cau_hoi from(select nhom_cau_hoi ,gender,sum(diem_so) from (select nhom_cau_hoi,nhom_diem, tra_loi,gender from (select nhom_cau_hoi,nhom_diem,tra_loi,account from (select nhom_cau_hoi ,ma_cau_hoi,nhom_diem from cau_hoi_neo ) as a
      left outer join
     (select ma_cau_hoi,tra_loi,account from tra_loi_neo where account=%s  and (tra_loi is not null or tra_loi !='')) as b on a.ma_cau_hoi = b.ma_cau_hoi ) as c
    left outer join
      (select username,gender from account) as d on c.account = d.username) as e
      left outer join
      (select *from quy_doi_diem) as f on e.tra_loi = f.tra_loi and e.nhom_diem = f.nhom
    group by nhom_cau_hoi,gender order by sum desc limit 1) as g
   left outer join 
   (select *from bang_nhan_cach ) as h 
   on g.gender = h.gender and g.nhom_cau_hoi = h.ma_nhom) as k
   left outer join
   (select ten_nhom, ma_nhom,thang_do,dien_giai,huong_nghiep from dien_giai_neo ) as l 
   on l.thang_do = k.thang_do and k.nhom_cau_hoi = l.ma_nhom) as nk""", (user,))
    rows_count = cur.fetchone()
    con.commit()
    cur.close()
    con.close()
    return rows_count


def get_rows(display, start_w, user):
    con = get_conection()
    cur = con.cursor()
    cur.execute(
        f"""     select ten_nhom,k.sum,k.thang_do, dien_giai,huong_nghiep from (select case when sum < thap 
   then 'thap'
   when sum >= thap and sum <= cao 
   then 'trung_binh'
   when sum > cao 
   then 'cao'
   else 'error'
   end as thang_do,nhom_cau_hoi,sum from(select nhom_cau_hoi ,gender,sum(diem_so) from (select nhom_cau_hoi,nhom_diem, tra_loi,gender from (select nhom_cau_hoi,nhom_diem,tra_loi,account from (select nhom_cau_hoi ,ma_cau_hoi,nhom_diem from cau_hoi_neo ) as a
      left outer join
     (select ma_cau_hoi,tra_loi,account from tra_loi_neo where account=%s and (tra_loi is not null or tra_loi !='')) as b on a.ma_cau_hoi = b.ma_cau_hoi ) as c
    left outer join
      (select username,gender from account) as d on c.account = d.username) as e
      left outer join
      (select *from quy_doi_diem) as f on e.tra_loi = f.tra_loi and e.nhom_diem = f.nhom
    group by nhom_cau_hoi,gender order by sum desc limit 1) as g
   left outer join 
   (select *from bang_nhan_cach ) as h 
   on g.gender = h.gender and g.nhom_cau_hoi = h.ma_nhom) as k
   left outer join
   (select ten_nhom, ma_nhom,thang_do,dien_giai,huong_nghiep from dien_giai_neo ) as l 
   on l.thang_do = k.thang_do and k.nhom_cau_hoi = l.ma_nhom """, (user,))
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
        table = 'cau_hoi_riasec'
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
            rows_count = count_rows(user)
            rows = get_rows(display, start_w, user)
            sum_page = (int(rows_count[0]) / display) + 1
            row = []
            for ro in rows:
                row.append(list(ro))
            page = '{"product":'
            objects_list = []
            cols = ["ten_nhom", "diem_so", "thang_do", "dien_giai", "huong_nghiep"]
            with ThreadPoolExecutor(max_workers=1) as executor:
                futures = [executor.submit(convert_row, i, row, cols) for i in range(len(row))]
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
