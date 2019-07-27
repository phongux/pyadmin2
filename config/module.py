import importlib, pyadmin.conn
importlib.reload(pyadmin.conn)
from pyadmin.conn import conn
import psycopg2
import psycopg2.extras
import psycopg2.extensions

class Module:

    project = "/wsgi/pyadmin2"
    control = f"{project}/control"
    js = "/pyadmin2/js"
    bootstrap = "/pyadmin2/bootstrap"
    load = f"{project}/load"
    save = f"{project}/save"

    csshead = """
              <style data-jsfiddle="common">
                .handsontable .currentRow {
                  background-color: #E7E8EF;
                }
                .handsontable .currentCol {
                  background-color: #F9F9FB;
                }
                #ui-datepicker-div{z-index:9000;}
                #datepicker{z-index:9000;}
                #example1{z-index:1;}
              </style>"""
    head = """<!doctype html>
                <html>
                    <head>
                        <meta charset='utf-8'>"""

    csscheckbox = """.multiselect-container>li>a>label {
      padding: 4px 20px 3px 20px;
    }"""

    headlink = f"""<script type="text/javascript" src="{js}/jquery.js"></script>
    <script type="text/javascript" src="{bootstrap}/js/bootstrap.js"></script>
    <!--<script type="text/javascript" src="{bootstrap}/js/dropdowns-enhancement.js"></script>
    <script type="text/javascript" src="{bootstrap}/js/bootstrap-multiselect.js"></script>-->
    <link rel="stylesheet" href="{bootstrap}/css/bootstrap.css" type="text/css">
    <!--<link rel="stylesheet" href="{bootstrap}/css/dropdowns-enhancement.css" type="text/css">
    <link rel="stylesheet" href="{bootstrap}/css/bootstrap-multiselect.css" type="text/css"/>-->
    <script type="text/javascript" src="{js}/jquery.bootpag.min.js"></script>
    <script type="text/javascript" data-jsfiddle="common" src="{js}/handsontable.full.js"></script>
    <link data-jsfiddle="common" rel="stylesheet" media="screen" href="{js}/handsontable.full.css" type="text/css">
    <!-- the below is only needed for DateCell (uses jQuery UI Datepicker) -->
    <script type="text/javascript" src="{js}/jquery-ui.js"></script>
    <link rel="stylesheet" href="{js}/jquery-ui.css" type="text/css">
                <style data-jsfiddle="common">
                .handsontable .currentRow {{
                background-color: #E7E8EF;
                }}
    
                .handsontable .currentCol {{
                background-color: #F9F9FB;
                }}
                #ui-datepicker-div{{z-index:9000;}}
                #datepicker{{z-index:9000;}}
                #example1{{z-index:1;}}
                </style>
            <script>
                $("#datepicker").datepicker();
                $("#format").change(function() {{
                $("#datepicker").datepicker( "option", "dateFormat", $( this ).val());
                }});
            </script>"""
    def connect(self):
    con = psycopg2.connect(conn)
    cur = con.cursor()

    menuhead = """<nav class="navbar navbar-expand-sm navbar-dark fixed-top bg-dark">
                        <ul class="navbar-nav">"""
    menuadmin = ""
    cur.execute("""Select fid,menu1,link from admin_first_menu order by id""")
    ps_admin_menu1 = cur.fetchall()
    cur.execute("""Select fid,menu1,link from first_menu order by id""")
    ps_menu1 = cur.fetchall()

    for row_admin1 in ps_admin_menu1:
        if row_admin1[0] == None:
            id = 0
        else:
            id = row_admin1[0]
        cur.execute(f"""Select menu2,link from admin_second_menu where first_menu_id = {id} order by id """)
        ps_admin_menu2 = cur.fetchall()
        if len(ps_admin_menu2) > 0:
            menuadmin += f"""
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" data-toggle="dropdown" href='{row_admin1[2]}' data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        {row_admin1[1]}
                        <b class="caret"></b>
                    </a>
                    <ul class="dropdown-menu">"""
            for row_admin2 in ps_admin_menu2:
                menuadmin += f"""
                    <li class='dropdown-item'>
                        <a class='dropdown-item' href='{row_admin2[1]}'>
                            {row_admin2[0]}
                        </a>
                    </li>"""
            menuadmin += """</ul></li>"""
        else:
            menuadmin += f"""
                <li class="nav-item">
                    <a class="nav-link" href='{row_admin1[2]}'>
                        {row_admin1[1]}
                    </a>
                </li>"""
    for row1 in ps_menu1:
        if row1[0] == None:
            id2 = 0
        else:
            id2 = row1[0]
        cur.execute(f"""Select menu2,link from second_menu where first_menu_id = {id2} order by id """)
        ps_menu2 = cur.fetchall()
        if len(ps_menu2) > 0:
            menuadmin += f"""
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" data-toggle="dropdown" href='{row1[2]}'>
                        {row1[1]}
                        <b class="caret"></b>
                    </a>"""
            menuadmin += """<ul class="dropdown-menu">"""
            for row2 in ps_menu2:
                menuadmin += f"""
                    <li class='dropdown-item'>
                        <a  class="dropdown-item" href='{row2[1]}'>
                            {row2[0]}
                        </a>
                    </li>"""
            menuadmin += """</ul></li>"""
        else:
            menuadmin += f"""
                <li class="nav-item">
                    <a class="nav-link" href='{row1[2]}'>
                        {row1[1]}
                    </a>
                </li>"""
    menuuser = ""
    cur.execute("""Select fid,menu1,link from first_menu order by id""")
    ps_menu1 = cur.fetchall()
    for row1 in ps_menu1:
        if row1[0] == None:
            id3 = 0
        else:
            id3 = row1[0]
        cur.execute(f"""Select menu2,link from second_menu where first_menu_id = {id3} order by id """)
        ps_menu2 = cur.fetchall()
        if len(ps_menu2) > 0:
            menuuser += f"""
                <li class="dropdown">
                    <a class="dropdown-toggle" data-toggle="dropdown" href='{row1[2]}' data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        {row1[1]}
                        <b class="caret"></b>
                     </a>"""
            menuuser += """<ul class="dropdown-menu">"""
            for row2 in ps_menu2:
                menuuser += f"""
                    <li class='dropdown-item'>
                        <a class="dropdown-item" href='{row2[1]}'>
                            {row2[0]}
                        </a>
                    </li>"""
            menuuser += """</ul></li>"""
        else:
            menuuser += f"""
                <li class="nav-link" >
                    <a class="nav-link" href='{row1[2]}'>
                        {row1[1]}
                    </a>
                </li>"""
    menufoot = """</ul>
                    </nav>"""
    con.commit()
    cur.close()
    con.close()
