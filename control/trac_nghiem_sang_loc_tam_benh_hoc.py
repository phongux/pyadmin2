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

def insert_answer(user):
    ma_de_thi = f"{user}{time.time()}"
    con = get_connection()
    cur = con.cursor()
    cur.execute(f"insert into tra_loi_sang_loc_tam_ly(ma_de_thi,ma_cau_hoi,account) select '{ma_de_thi}' as ma_de_thi,ma_cau_hoi,'{user}' as account from cau_hoi_sang_loc_tam_ly  order by id ")
    con.commit()
    cur.close()
    con.close()


def delete_answer(user):
    con = get_connection()
    cur = con.cursor()
    cur.execute(f"delete from tra_loi_sang_loc_tam_ly where account=%s ",(user,))
    con.commit()
    cur.close()
    con.close()

def get_ma_phieu(user):
    con = get_connection()
    cur = con.cursor()
    cur.execute(f"select ma_de_thi,account,status from tra_loi_sang_loc_tam_ly group by ma_de_thi,account,status having account=%s and status is null limit 1",(user,))
    row = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return row

def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    post = request.POST
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
        birthday = session['birthday']
        gender = session['gender']
        depart = session['depart']
        company = session['company']
        ps = get_account(user, passwd, captra)
        if int(ps[0][2]) > 0:
            delete_answer(user)
            insert_answer(user)
            ma_phieus = get_ma_phieu(user)
            ma_phieu = ma_phieus[0][0]
            if not 'display' in post:
                display = 200
            else:
                display = post['display']
            saveurl = f"""'{save}/save_sang_loc_tam_benh_hoc'"""
            loadurl = f"""'{load}/load_sang_loc_tam_benh_hoc'"""
            page = ""
            page += head
            page += "<title>Sàng lọc tâm bệnh học</title>"
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
                <h2>PHIẾU HỎI THÔNG TIN</h2>
				<p>Mã phiếu:{ma_phieu} </br>
                    Chào các em!
                    Chúng tôi đang tìm hiểu về những khó khăn tâm lý của học sinh trung học phổ thông. Những ý kiến của các em sẽ là đóng góp quý báu giúp chúng tôi thực hiện đề tài nghiên cứu này. Chúng tôi xin đảm bảo những thông tin thu thập được từ các em sẽ hoàn toàn được giữ bí mật và chỉ phục vụ cho nghiên cứu khoa học. Cám ơn sự giúp đỡ của các em rất nhiều!
                </p>			
                <p><b>A. Thông tin cá nhân</b>
                <p> Account : {user} </p>
				<p> Giới tính: {gender}  , Năm sinh: {birthday} </p>
				<p> Lớp: {depart}  Trường: {company}
                <p><b> B. Các khó khăn tâm lý </b></p>
                    <b><i>Dưới đây là những câu hỏi về các khó khăn mà em gặp phải trong sáu tháng vừa qua. Em hãy điền đáp án phù hợp với em nhất.(Điền số vào cột trả lời)</i></b>
                </p>
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
        <p><b><i>Chân thành cảm ơn em rất nhiều!</i></b></p>
        <script>
        var display = {display};
        var colu = ["id","ma_cau_hoi","tra_loi","cau_hoi","ma_nhom_cau_hoi"];
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
        startRows: 8,
        startCols: 3,
        currentRowClassName: 'currentRow',
        currentColClassName: 'currentCol',
        autoWrapRow: true,
        rowHeaders: true,
        colHeaders: ["Id","Mã câu hỏi","Trả lời","Câu hỏi","Nhóm"],
        columns: [{{readOnly: true}},{{readOnly: true}},{{}},
        {{    
            type:'numeric',readOnly: true,renderer: 'html'
        }},{{readOnly: true}}],
        colWidths: [0.1,0.1,10,300,0.1],		
        manualColumnResize: true,
        manualRowResize: true,		
        autoColumnSize : true,
		    cells: function(row, col, prop) {{
      var cellProperties = {{}};

      if (row === 0) {{
        cellProperties.readOnly = true;
      }}

      return cellProperties;
    }},
	  //mergeCells: [
    //{{row: 0, col: 2, rowspan: 1, colspan: 2}},    
  //],
        stretchH: 'all',	
        minSpareCols: 0,
        minSpareRows: 1,
        contextMenu: true,
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
                var request = $.ajax({{
            url: {saveurl},
            //contentType: "application/json; charset=utf-8",
            async: false,
            method: "POST",
            //dataType: "html",
            crossDomain: true,
            data: {{
                update:update,
                insert:insert,
                lenupdate:update.length,
                leninsert:insert.length,
            }},
            cache: false
        }});
        request.done(function (msg) {{
            if (JSON.parse(msg).result === 'ok') {{
                var page_num = parseInt(document.getElementById("page_number").innerText);
                loadPage(page_num);                        
                autosaveNotification = setTimeout(function () {{
                    $console.text('Changes will be autosaved ');
                }}, 500);
            }}
        }});
        request.fail(function (jqXHR, textStatus) {{
            $console.html("<font color='red'>Data save error:</font>");
        }});
        /*$.ajax({{
            url: {saveurl},
            dataType: 'json',
            type: 'POST',
            //data: {{"changes": change}}, // contains changed cells' data
            data: {{
                update:update,
                insert:insert,
                lenupdate:update.length,
                leninsert:insert.length,
            }},
            success: function (res) {{
                if (res.result === 'ok') {{
                    //alert(res);
                    //$console.text('Autosaved (' + change.length + ' cell' + (change.length > 1 ? 's' : '') + ')');
                    //document.getElementById("load_dog").click();
                    var page_num = parseInt(document.getElementById("page_number").innerText);
                    loadPage(page_num);                        
                    autosaveNotification = setTimeout(function () {{
                        $console.text('Changes will be autosaved ');
                    }}, 1000);
                }}
                else{{
                    $console.html("<font color='red'>Data save error</font>");}}
                }},
                error: function (res) {{
                    autosaveNotification = setTimeout(function () {{
                        $console.html("<font color='red'>Data save error:</font>");
                    }}, 
                    1000);
                }}
            }});*/
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
$parent.find('button[name=reset]').click(function () {{
    $.ajax({{
        url: 'php/reset.php',
        success: function () {{
            $parent.find('button[name=load]').click();
        }},
        error: function () {{
            $console.text('Data reset failed');
        }}
    }});
}});
$parent.find('input[name=autosave]').click(function () {{
    if ($(this).is(':checked')) {{
        $console.text('Changes will be autosaved');
    }}
    else {{
        $console.text('Changes will not be autosaved');
    }}
}});
hot.selectCell(3,3);
//hot.updateSettings({{columns: [{{data:1}},{{data:2,type:"password"}},{{data:3}},{{data:4}},{{data:5}},{{data:6}}] }});


function loadPage(page_num){{

    $.ajax({{
        url: {loadurl},
        data: JSON.parse(
            JSON.stringify({{
                "page":page_num,
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
            
            if(page_num > Math.round(res.sum_page)){{ page_num = Math.round(res.sum_page)}}
            $(".page2").html("<strong>Page <span id='page_number'>" + page_num + "</span> / <span id='total_page'>" + Math.round(res.sum_page)+"</span></strong>");
            $('.demo2').bootpag({{
                total: res.sum_page,
                page: page_num,
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
                if(page_num > Math.round(res.sum_page)){{ page_num = Math.round(res.sum_page)}}
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
            }})               
        }}
    }});    
}};
function firstRowRenderer(instance, td, row, col, prop, value, cellProperties) {{
  Handsontable.renderers.TextRenderer.apply(this, arguments);
  td.style.fontWeight = 'bold';
  td.style.color = 'green';
  td.style.background = '#CEC';
}}

function safeHtmlRenderer(instance, td, row, col, prop, value, cellProperties) {{
  var escaped = Handsontable.helper.stringify(value);
  escaped = strip_tags(escaped, '<em><b><strong><a><big>'); //be sure you only allow certain HTML tags to avoid XSS threats (you should also remove unwanted HTML attributes)
  td.innerHTML = escaped;

  return td;
}}

function coverRenderer (instance, td, row, col, prop, value, cellProperties) {{
  var escaped = Handsontable.helper.stringify(value),
    img;

 if (escaped.indexOf('http') === 0) {{
    img = document.createElement('IMG');
    img.src = value;

    Handsontable.dom.addEvent(img, 'mousedown', function (e){{
      e.preventDefault(); // prevent selection quirk
    }});

    Handsontable.dom.empty(td);
    td.appendChild(img);
  }}
  else {{
    // render as text
    Handsontable.renderers.TextRenderer.apply(this, arguments);
  }}

  return td;
}}
  hot.updateSettings({{
    cells: function (row, col) {{
      var cellProperties = {{}};
		var rowCheck = hot.getData()[row][4];
      if (rowCheck=== 'ch') {{
        cellProperties.readOnly = true;
		cellProperties.renderer = firstRowRenderer;
      }}
	  else{{
		cellProperties.type = 'dropdown';
        if (rowCheck ==='11'||rowCheck ==='12'){{
			cellProperties.source = [0,1,2,3,4,5,6,7,8,9];
		}}
        else if (rowCheck ==='18'){{
			cellProperties.source = [0,1,2,3,4];
		}}
        else{{
			cellProperties.source = [0,1,2,3];
		}}
		
		cellProperties.strict = true;
		cellProperties.allowInvalid = false;
	  }}
  
      return cellProperties;
    }}
  }},

  );

</script>
</body>
</html>"""
        else:
            page = pyadmin.login.login_again
    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    return response(environment, start_response)


session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
