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
            loadurl = f"""'{load}/load_account_manager'"""
            saveurl = f"""'{save}/save_account_manager'"""
            page = ""
            page += head
            page += "<title>Account manager</title>"
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
                <h2>Thiết lập tài khoản</h2>
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
        var colu = ["id","gmail","account_password","fullname","gender","depart","company","birthday"];
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
        colHeaders: ["id","email","Mật khẩu","Họ và tên","Giới tính","Lớp học(Bộ phận)","Trường học (cty)","Ngày sinh"],
        columns: [{{readOnly: true}},{{}},{{}},{{}},{{}},{{}},{{}},{{}}],
        colWidths: [0.1,30,30,30,30,30,30,30],       
        manualColumnResize: true,
        manualRowResize: true,      
        autoColumnSize : true,
        stretchH: 'all',    
        hiddenColumns: true,            
        minSpareCols: 0,
        minSpareRows: 0,
        contextMenu: true,beforeRemoveRow: function(index, amount) {{
                var dellist=[];
                for(var i=0; i<amount; i++){{
                    dellist.push(hot.getData()[index +i][colu.indexOf("id")]);
                }}
                $.ajax({{
                    url: {saveurl},
                    data: {{delete:dellist}}, // returns all cells' data
                    dataType: 'json',
                    type: 'POST',
                    success: function(res) {{
                    if (res.result === 'ok') {{
                        $console.text('Data saved');
                        var page_num = parseInt(document.getElementById("page_number").innerText);
                        loadPage(page_num);
                    }}
                    else {{
                        $console.text('Save error');
                    }}
                }},
                error: function () {{
                    $console.text('Save error');
                }}
            }});        
        }},              
        afterChange: function (change, source) {{
            var data;
            if (source === 'loadData' || !$parent.find('input[name=autosave]').is(':checked')) {{
                return;
            }}
            data = change[0];
            var update = [],insert=[],rows=[],unique=[];
            for (var i=0;i<change.length;i++){{
                if (hot.getData()[change[i][0]][colu.indexOf("id")] == null){{
                    rows.push(change[i][0]);
                }}
                else{{
                    update.push({{"id":hot.getData()[change[i][0]][colu.indexOf("id")],"column":colu[change[i][1]],"value":change[i][3]}});
                }}
            }}
            if (rows.length >0) {{  
                for(var i in rows){{
                    if(unique.indexOf(rows[i]) === -1){{
                        unique.push(rows[i]);
                    }}
                }}                
                for (var i in unique){{
                    var son = {{}};
                    for (var k in colu){{
                        son[colu[k]] = hot.getData()[unique[i]][k]
                    }}
                    insert.push(son);
                }}
            }}
            // transform sorted row to original row
            //data[0] = hot.sortIndex[data[0]] ? hot.sortIndex[data[0]][0] : data[0];
            clearTimeout(autosaveNotification);
            $.ajax({{
                url: {saveurl},
                dataType: 'json',
                type: 'POST',
                data: {{
                    update:update,
                    lenupdate:update.length
                }},
                success: function (res) {{
                    if (res.result === 'ok') {{
                        var page_num = parseInt(document.getElementById("page_number").innerText);
                        loadPage(page_num);                        
                        autosaveNotification = setTimeout(function () {{
                            $console.text('Changes will be autosaved ');
                        }}, 500);
                    }}
                    else{{
                        $console.html("<font color='red'>Data save error</font>");}}
                    }},
                    error: function (res) {{
                        autosaveNotification = setTimeout(function () {{
                            $console.html("<font color='red'>Data save error:</font>");
                        }}, 
                        500);
                    }}
                }});
            }}
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
