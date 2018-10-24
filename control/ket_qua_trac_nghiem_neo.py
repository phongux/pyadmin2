from beaker.middleware import SessionMiddleware
import importlib
import re
import time
import psycopg2
import pyadmin.module
from datetime import datetime, date
import pyadmin.sess
import pyadmin.conn, pyadmin.login

importlib.reload(pyadmin.conn)
importlib.reload(pyadmin.login)
importlib.reload(pyadmin.sess)
from pyadmin.module import head, headlink, menuadmin, menuuser, load, save, menuhead, menufoot


def get_connection():
    connection = psycopg2.connect(pyadmin.conn.conn)
    return connection


def get_account(user, passwd, captra):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "select username,account_password,account_level from account where username=%s and account_password=%s and captra=%s ",
        (user, passwd, captra))
    ps = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return ps

def get_ma_phieu(user):
    con = get_connection()
    cur = con.cursor()
    cur.execute(f"select ma_de_thi,account,status from tra_loi_neo group by ma_de_thi,account,status having account=%s and status is null limit 1",(user,))
    row = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return row

def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    params = request.params
    post = request.POST
    res = Response()

    # Get the session object from the environ
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
        if int(ps[0][2]) > 0:
            if not 'display' in post:
                display = 200
            else:
                display = post['display']
            loadurl = f"""'{load}/load_ket_qua_trac_nghiem_neo'"""
            page = ""
            page += head
            page += "<title>NEO</title>"
            page += headlink
            page += """
                </head>
                <body>"""
            page += menuhead
            if int(ps[0][2]) == 2:
                page += menuadmin
            else:
                page += menuuser
            page += menufoot
            # for in this case need add more filter duplicate row in table home;
            page += f"""
                <br /><br /><br />
                <h2>Trac nghiem NEO </h2>
                <p> Account : {user} </p>
                <br />
        <p>
            <button name="load" id="load_dog">Load</button>
            <button name="reset">Reset</button>
            <label>
                <input id="autosave" type="checkbox" name="autosave" checked="checked" autocomplete="off">
                Autosave
            </label>
        </p>
        <div>
            <span class="page2">No page selected</span> |
            <strong>
                <span id="exampleConsole" class="console">
                    Click "Load" to load data from server 
                </span>
            </strong> 
        </div>
        <div id="example1" style="width:100%; height: 500px; overflow: hidden"></div>
        <nav class="demo2"></nav>
        <script>
        var display = {display};
        var colu = ["ten_nhom", "diem_so","thang_do", "dien_giai", "huong_nghiep"];
    var $$ = function(id) {{
        return document.getElementById(id);
    }},
    autosave = $$('autosave'),
    $container = $("#example1"),
    $console = $("#exampleConsole"),
    $parent = $container.parent(),
    autosaveNotification,
    hot;
    hot = new Handsontable($container[0], {{
        columnSorting: true,
        startRows: 1,
        startCols: 3,
        currentRowClassName: 'currentRow',
        currentColClassName: 'currentCol',
        autoWrapRow: true,
        rowHeaders: true,
        colHeaders: ["Tên nhóm","Diem","Thang đo", "Diễn giải", "Hướng nghiệp"],
        columns: [{{readOnly: true}},{{readOnly: true}},{{readOnly: true}},{{readOnly: true}},{{readOnly: true}}],
        colWidths: [50,15,20,300,300],		
        manualColumnResize: true,
        manualRowResize: true,		
        autoColumnSize : true,
        stretchH: 'all',	
        hiddenColumns: true,			
        minSpareCols: 0,
        minSpareRows: 0,
        contextMenu: true
    }});
    
    $parent.find('button[name=load]').click(function () {{
        $.ajax({{
            url: {loadurl},
            data: JSON.parse(
                JSON.stringify({{
                    "display":display
                }})
            ),
            dataType: 'json',
            type: 'POST',					
            success: function (res) {{
                var data = [], row;
                for (var i = 0, ilen = res.product.length; i < ilen; i++) {{
                    row = [];
                    for(var m in colu){{
                    row[m] = res.product[i][colu[m]];
                }}
                data[res.product[i].idha - 1] = row;
            }}
            $console.text('Data loaded');
            hot.loadData(data);
              
            $(".page2").html("<strong>Page <span id='page_number'>1</span> / <span id='total_page'>" + Math.round(res.sum_page)+"</span></strong>");
            $('.demo2').bootpag({{
                total: res.sum_page,
                page: 1,
                maxVisible: 10,
                //href:'../demo/account_manager.py?page={{{{number}}}}',
                leaps: false,
                firstLastUse: true,
                first: '←',
                last: '→',
                wrapClass: 'pagination',
                activeClass: 'active',
                disabledClass: 'disabled',
                nextClass: 'next',
                prevClass: 'prev',
                lastClass: 'last',
                firstClass: 'first'
            }}).on('page', function(event, num){{
                $(".page2").html("<strong>Page <span id='page_number'>" + num + "</span> / <span id='total_page'>" + Math.round(res.sum_page)+"</span></strong>"/* + res.test */);
                $.ajax({{
                    url: {loadurl},
                    data: JSON.parse(
                        JSON.stringify({{
                            "page":num,
                            "display":display
                        }})
                    ),
                    dataType: 'json',
                    type: 'POST',
                    success: function (res) {{
                        var data = [], row;
                        for (var i = 0, ilen = res.product.length; i < ilen; i++) {{
                            row = [];
                            for(var m in colu){{
                               row[m] = res.product[i][colu[m]];
                            }}
                            data[res.product[i].idha - 1] = row;
                        }}
                        $console.text('Data loaded');
                        hot.loadData(data);
                    }}
                }});
            }});                  
        }}
    }});
            }}).click(); // execute immediately


hot.selectCell(3,3);
//hot.updateSettings({{columns: [{{data:1}},{{data:2,type:"password"}},{{data:3}},{{data:4}},{{data:5}},{{data:6}}] }});


</script>
</body>
</html>"""
        else:
            page = pyadmin.login.login_again
    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    return response(environment, start_response)


session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
