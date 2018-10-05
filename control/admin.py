from beaker.middleware import SessionMiddleware
import importlib
import re
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
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "select username,account_password,account_level from account where username=%s and account_password=%s and captra=%s ",
            (user, passwd,captra))
        ps = cur.fetchall()
        con.commit()
        cur.close()
        con.close()
        if len(ps) == 0:
            page = pyadmin.login.login_again
        else:
            if int(ps[0][2]) == 2:
                if not 'display' in post:
                    display = 200
                else:
                    display = post['display']
                if 'hidecols' not in post:
                    hidecols = []
                else:
                    hidecols = post.getall('hidecols')
                if 'hidefils' not in post:
                    hidefils = []
                else:
                    hidefils = post.getall('hidefils')
                if 'orderby' not in post:
                    orderby = ['1']
                else:
                    orderby = post.getall('orderby')
                if 'by' not in post:
                    by = 'asc'
                else:
                    by = post['by']
                que = ""
                if 'table' in post:
                    if post['table'] != "":
                        table = post['table']
                        con = get_connection()
                        cur = con.cursor()
                        cur.execute(
                            f"select count(*) from information_schema.tables where table_name='{post['table']}' ")
                        check = cur.fetchone()
                        con.commit()
                        cur.close()
                        con.close()
                        if check[0] > 0:
                            # table exists in database
                            con = get_connection()
                            cur = con.cursor()
                            cur.execute(f"select count(*) from {table} limit 1")
                            que = f"select *from {table} "
                            countrows = cur.fetchone()
                            con.commit()
                            cur.close()
                            con.close()
                            if countrows[0] == 0:  # no records in table, table is empty
                                con = get_connection()
                                cur = con.cursor()
                                cur.execute(
                                    f"select column_name, data_type from information_schema.columns "
                                    f"where table_name = '{post['table']}' ")
                                rws = cur.fetchall()
                                con.commit()
                                cur.close()
                                con.close()
                                cols = [desc[0] for desc in rws if desc[0] not in hidecols]
                                # colHeaders =[co.title().replace("_"," ") for co in cols]
                                data_types = [desc[1] for desc in rws if desc[0] not in hidecols]
                                colslist = [desc[0] for desc in cur.description]
                                filcols = [fils for fils in cols if fils not in hidefils]
                                if 'movecols' in post:
                                    if len(post.getall('movecols')) != 0:
                                        movecols = f",movecols:{str(post.getall('movecols'))}"
                                        cols = [co for co in post.getall('movecols') if co not in hidecols]
                                        que = f"""select {",".join(cols)} from  {table}"""
                                else:
                                    movecols = ""
                            # records in table, table is not empty
                            else:
                                con = get_connection()
                                cur = con.cursor()
                                cur.execute(f"select * from {table} limit 1")
                                cols = [desc[0] for desc in cur.description if desc[0] not in hidecols]
                                daty = cur.fetchone()
                                con.commit()
                                cur.close()
                                con.close()
                                que = f"select *from {table} "
                                data_types = [type(val).__name__ for index, val in enumerate(daty)]
                                colslist = [desc[0] for desc in cur.description]
                                filcols = [fils for fils in cols if fils not in hidefils]
                                if 'movecols' in post:
                                    if len(post.getall('movecols')) != 0:
                                        movecols = f",movecols:{str(post.getall('movecols'))}"
                                        cols = [co for co in post.getall('movecols') if co not in hidecols]
                                        con = get_connection()
                                        cur = con.cursor()
                                        cur.execute(f"""select {",".join(cols)} from {table} limit 1""")
                                        colslist = [desc[0] for desc in cur.description]
                                        con.commit()
                                        cur.close()
                                        con.close()
                                        que = f"""select {",".join(cols)} from {table}"""
                                        filcols = [fils for fils in cols if fils not in hidefils]
                                else:
                                    movecols = ""
                        else:  # table does not exits in database, only for query sql
                            table = post['table']
                            con = get_connection()
                            cur = con.cursor()
                            cur.execute(f"select count(*) from settings where tablename='{table}' ")
                            check2 = cur.fetchone()
                            con.commit()
                            cur.close()
                            con.close()
                            if check2[0] > 0:
                                con = get_connection()
                                cur = con.cursor()
                                cur.execute(f"select query from settings where tablename='{table}' limit 1")
                                check3 = cur.fetchone()
                                con.commit()
                                cur.close()
                                con.close()
                                con = get_connection()
                                cur = con.cursor()
                                cur.execute(f"select count(*) from ({check3[0]}) as jotikaandmendaka")
                                check5 = cur.fetchone()
                                con.commit()
                                cur.close()
                                con.close()
                                if check5[0] > 0:
                                    con = get_connection()
                                    cur = con.cursor()
                                    cur.execute(f"select * from ({check3[0]}) as jotikaandmendaka limit 1")
                                    que = check3[0]
                                    cols = [desc[0] for desc in cur.description if desc[0] not in hidecols]
                                    daty = cur.fetchone()
                                    con.commit()
                                    cur.close()
                                    con.close()
                                    data_types = [type(val).__name__ for index, val in enumerate(daty)]
                                    colslist = [desc[0] for desc in cur.description]
                                    filcols = [fils for fils in cols if fils not in hidefils]
                                    if 'movecols' in post:
                                        if len(post.getall('movecols')) > 0:
                                            movecols = f",movecols:{str(post.getall('movecols'))}"
                                            cols = [co for co in post.getall('movecols') if co not in hidecols]
                                            con = get_connection()
                                            cur = con.cursor()
                                            cur.execute(
                                                f"""select {",".join(cols)} from ({check3[0]} 
                                                as jotikaandmendaka limit 1"""
                                            )
                                            que = check3[0]
                                            colslist = [desc[0] for desc in cur.description]
                                            con.commit()
                                            cur.close()
                                            con.close()
                                            filcols = [fils for fils in cols if fils not in hidefils]

                                    else:  # no row in query
                                        movecols = ""
                                else:
                                    cols = []
                                    data_types = []
                                    table = ""
                                    colslist = []
                                    filcols = []
                                    movecols = ""
                                    que = ""
                            else:
                                cols = []
                                data_types = []
                                table = ""
                                colslist = []
                                filcols = []
                                movecols = ""
                                que = ""
                    else:  # table =""

                        cols = []
                        data_types = []
                        table = ""
                        colslist = []
                        filcols = []
                        movecols = ""
                        que = ""
                else:  # no table in post
                    cols = []
                    data_types = []
                    table = ""
                    colslist = []
                    filcols = []
                    movecols = ""
                    que = ""
                if 'table' in params:
                    table = params.getall('table')[0]
                colHeaders = [co.title().replace("_", " ") for co in cols]
                con = get_connection()
                cur = con.cursor()
                cur.execute("select tablename,query from settings order by id")
                lst = cur.fetchall()
                con.commit()
                cur.close()
                con.close()
                ops = ""
                for ls in lst:
                    # ops += "<option value='%s'>"%l[0]
                    if ls[0] == table:
                        ops += f"""<option value="{ls[0]}" selected="selected">{ls[0]}</option>"""
                    else:
                        ops += f"""<option value="{ls[0]}">{ls[0]}</option>"""
                types = {}
                for i in range(len(cols)):
                    types[cols[i]] = data_types[i]
                data = []
                grofil = ""
                for fil in filcols:
                    fil_re = fil.title().replace("_", " ")
                    if types[fil] == 'int':
                        grofil += f"""
                            {fil_re} > <input class="input-mini" name='mor{fil}' value=''/> 
                            and {fil_re} < <input class="input-mini" name='les{fil}' value=''/> || """
                    elif types[fil] == 'datetime' or types[fil] == 'date':
                        grofil += f"""
                            {fil_re} > <input class="input-mini" name='mor{fil}' value=''/> 
                            and {fil_re} < <input class="input-mini" name='les{fil}' value=''/> || """
                    else:
                        grofil += f""" 
                        ilike <input class="input-mini" name='fil{fil}' value=''/>||
                        {fil_re} not ilike <input class="input-mini" name='notfil{fil}' value=''/>|| """

                    grofil += f"""{fil_re} 
                        <select name="{fil}null">
                            <option value=""></option>
                            <option value="null">Empty</option>
                            <option value="not_null">not empty</option>
                        </select> """
                    if f'mor{fil}' in post:
                        data.append(f""" mor{fil}:"{post[f"mor{fil}"]}" """)
                    if f'les{fil}' in post:
                        data.append(f""" les{fil}:"{post[f"les{fil}"]}" """)
                    if f'fil{fil}' in post:
                        data.append(f""" fil{fil}:"{post[f"fil{fil}"]}" """)
                    if f'{fil}null' in post:
                        data.append(f""" {fil}null:"{post[f"{fil}null"]}" """)
                if len(data) > 0:
                    send_data = "," + ",".join(data)
                else:
                    send_data = ""
                hidefilter = ""
                hidefilter += """
    				<div class="btn-group">
				        <button data-toggle="dropdown" class="btn dropdown-toggle"  data-placeholder="Hide filter">
					        Hide filter <span class="caret"></span>
				        </button>
					    <ul id="sortable3" class="connectedSortable dropdown-menu">
					"""
                for colsname in colslist:
                    colsname_re = colsname.title().replace("_", " ")
                    if colsname in hidefils:
                        hidefilter += f"""
                        <li class="ui-state-default">
                            <input type="checkbox" id="fil{colsname}" name="hidefils" value="{colsname}">
                            <label for="fil{colsname}" name="hidefils" value="{colsname}" checked>
                            {colsname_re}
                            </label>
                        </li>"""
                    else:
                        hidefilter += f"""
                            <li class="ui-state-default">
                                <input type="checkbox" id="fil{colsname}" name="hidefils" value="{colsname}">
                                <label for="fil{colsname}" name="hidefils" value="{colsname}" >
                                {colsname_re}
                                </label></li>"""

                hidefilter += """
					  <!-- Other items -->
					</ul>
				</div>"""
                columns = []
                for colname in cols:
                    if colname == 'id':
                        columns.append({'readOnly': 'true'})
                    elif colname == 'account_password':
                        columns.append({"type": "password"})
                    elif colname == 'update_time':
                        columns.append({'readOnly': 'true'})
                    elif colname == 'account_level':
                        columns.append({'type': 'numeric', 'allowEmpty': 'false'})
                    elif colname == 'username':
                        columns.append({'allowEmpty': 'false'})
                    elif colname == 'fid':
                        columns.append({'type': 'numeric', 'allowEmpty': 'false'})
                    else:
                        columns.append({})
                saveurl = f"""'{save}/save_admin'"""
                loadurl = f"""'{load}/load_admin'"""
                que_re = re.sub('\s+', ' ', que.replace('"', '\\"'))
                page = ""
                page += head
                page += "<title>Admin</title>"
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
                if 'year' in params:
                    year = params.getone('year')
                else:
                    year = datetime.today().year
                if table == f'home_{year}':
                    cur.execute(
                        f"delete from {table} where id not in (select max(id) from {table} group by report_date,agent)")
                page += f"""
                    <br /><br /><br />
				    <ul class="nav nav-tabs">
						<li class="active"><a href="{pyadmin.module.control}/account_manager">{table}</a></li>
					</ul>
					<h2>Table {table} </h2>
    				Order by: {",".join(orderby)}. Sort by: {by}. Hide columns: {",".join(hidecols)}	
    				| Hide filter: {",".join(hidefils)} + {movecols}  
    				<br />
				    <nav class='navbar navbar-default'>
					<form method="post" action="">								
					    <div class="btn-group col-sm-3">
						    <label class='btn-group' >Table:
								<input class='btn-group form-control' list="table" name="table" value="{table}"  onchange='if(this.value != 0) {{ this.form.submit(); }}'>
							    <datalist id="table">
									{ops}
								</datalist>
							</label> 
						</div> 	
                        <!--<select id="example-single-selected">
                            <option value="">test</option>
                            <option value="">test</option>
                        </select>-->
                        <div class="btn-group">
                        <button data-toggle="dropdown" class="btn dropdown-toggle"  data-placeholder="Move columns">
	                        Move columns <span class="caret"></span>
                        </button>
                        <ul id="sortable6" class="connectedSortable dropdown-menu">"""
                for colsname in colslist:
                    cols_re = colsname.title().replace("_", " ")
                    page += f"""
                        <li class="ui-state-default">
                            <input type="checkbox" id="move{colsname}" name="movecols" value="{colsname}">
                            <label for="move{colsname}" name="movecols" value="{colsname}" >
                                {cols_re}
                            </label>
                        </li>"""
                page += """
                    <!-- Other items -->
                    </ul>
                    </div>									 								
                    <div class="btn-group">
                    <button data-toggle="dropdown" class="btn dropdown-toggle"  data-placeholder="Hide column">
	                    Hide columns <span class="caret"></span>
                    </button>
                    <ul id="sortable1" class="connectedSortable dropdown-menu">"""
                for colsname in colslist:
                    cols_re = colsname.title().replace("_", " ")
                    page += f"""
                    <li class="ui-state-default">
                        <input type="checkbox" id="{colsname}" name="hidecols" value="{colsname}">
                        <label for="{colsname}" name="hidecols" value="colsname" >
                            {cols_re}
                        </label>
                    </li>"""
                page += """
                    <!-- Other items -->
                    </ul>
                    </div>	
                    <div class="btn-group">
                        <button data-toggle="dropdown" class="btn dropdown-toggle"  data-placeholder="Order by">
	                        Order by <span class="caret"></span>
                        </button>
                    <ul id="sortable2" class="connectedSortable dropdown-menu">"""
                for colsname in colslist:
                    cols_re = colsname.title().replace("_", " ")
                    page += f"""
                    <li class="ui-state-default">
                        <input type="checkbox" id="by{colsname}" name="orderby" value="{colsname}">
                        <label for="by{colsname}" name="orderby" value="{colsname}" >
                            {cols_re}</label>
                    </li>"""
                page += f"""
                    <!-- Other items -->
                    </ul>
                    </div>	
                    <div class="btn-group">
                        <button data-toggle="dropdown" class="btn dropdown-toggle"  data-placeholder="Sort by">
	                        Sort by <span class="caret"></span>
                        </button>
                        <ul class="dropdown-menu">
                            <li class="ui-state-default">
                                <input type="radio" id="asc" name="by" value="asc">
                                <label for="asc" name="by" value="asc" >asc</label>
                            </li>
                            <li class="ui-state-default">
                                <input type="radio" id="desc" name="by" value="desc">
                                <label for="desc" name="by" value="desc" >desc</label>
                            </li>
                            <!-- Other items -->
                        </ul>
                    </div>
                    <div id='filadv' style='display:none'>
                        {hidefilter}
                        {grofil}
                    </div>Show filter 
				        <input class="btn-group" type="checkbox" onclick="myFunction()"/>
			            <div class="btn-group col-sm-2">
				        <input class="btn-group form-control mr-sm-3" type="number" name ="display" value = {display} />
				    </div>
				    <input type="submit" id ="chon" value="Chon" />
				</div>
			</form>
			</nav>
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
        	<script>"""
                for hids in hidefils:
                    page += f"""$("#fil{hids}").click();"""
                # for c in cols:
                # page +="""$("#move%s").click();"""%c
                page += f"""
                /*$(document).ready(function() {{
                    $('#example-dropDown, #example-single-selected').multiselect({{
                        enableFiltering: true,
                        includeSelectAllOption: false,
                        disableIfEmpty: true,
                        multiple:false,
                        maxHeight: 400,
                        dropDown: true
                    }});
                }});*/
                function myFunction() {{
                    var x = document.getElementById('filadv');
                    if (x.style.display === 'none') {{
                        x.style.display = 'inline';
                    }} else {{
                        x.style.display = 'none';
                    }}
                }}			
                $( function() {{
                    $( "#sortable1, #sortable2,#sortable3,#sortable5 ,#sortable6").sortable({{
                        connectWith: ".connectedSortable"
                    }}).disableSelection();
                    $("ul, li").disableSelection();
                }} );
                var colu = {cols};
                emailValidator = function (value, callback) {{
                setTimeout(function(){{
                if (/.+@.+/.test(value)) {{
                    callback(true);
                }}
                else {{
                    callback(false);
                }}
            }}, 1000);
        }};				
        emptyValidator = function(value, callback) {{
            setTimeout(function(){{
            if (isEmpty(value)) {{ // isEmpty is a function that determines emptiness, you should define it
                callback(true);
            }} else {{
                callback(fasle);
            }}
            }}, 1000);    
        }}	    

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
            colHeaders: {str(colHeaders)},
            columns: {str(columns)},
            colWidths: [0.1,50,200,50,50,50,50],		
            manualColumnResize: true,
            manualRowResize: true,		
            autoColumnSize : true,
            stretchH: 'all',	
            hiddenColumns: true,			
		    minSpareCols: 0,
		    minSpareRows: 1,
		    contextMenu: true,
			beforeRemoveRow: function(index, amount) {{
			    var dellist=[];
			    for(var i=0; i<amount; i++){{
			        dellist.push(hot.getData()[index +i][colu.indexOf("id")]);
			    }}
			    //alert(dellist);
				$.ajax({{
					url: {saveurl},
					data: {{delete:dellist,table:"{table}"}}, // returns all cells' data
					dataType: 'json',
					type: 'POST',
					success: function(res) {{//alert(res);
					if (res.result === 'ok') {{
						$console.text('Data saved');
						//document.getElementById("load_dog").click();
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
			    //data: {{"changes": change}}, // contains changed cells' data
			    data: {{
			        update:update,
			        insert:insert,
			        lenupdate:update.length,
			        leninsert:insert.length,
			        table:"{table}",
			        cols:{str(cols)}
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
			    }});
            }}
		}});
		
		$parent.find('button[name=load]').click(function () {{
		    $.ajax({{
			    url: {loadurl},
                data: JSON.parse(
                    JSON.stringify({{
                        types:{str(types)},
                        "display":{display},
                        table:"{table}",
                        cols:{str(cols)},
                        orderby:{str(orderby)},
                        by:"{by}",
                        filcols:{filcols}{send_data}{movecols},
                        que:"{que_re}"
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
                                types:{str(types)},
                                "page":num,
                                "display":{display},
                                table:"{table}",
                                cols:{str(cols)},
                                orderby:{str(orderby)},
                                by:"{by}",
                                filcols:{filcols}{send_data}{movecols},
                                que:"{que_re}"}}
                            )
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
                    types:{str(types)},
                    "page":page_num,
                    "display":{display},
                    table:"{table}",
                    cols:{str(cols)},
                    orderby:{str(orderby)},
                    by:"{by}",
                    filcols:{filcols}{send_data}{movecols},
                    que:"{que_re}"}}
                )
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
                                types:{str(types)},
                                "page":num,
                                "display":{display},
                                table:"{table}",
                                cols:{str(cols)},
                                orderby:{str(orderby)},
                                by:"{by}",
                                filcols:{filcols}{send_data}{movecols},
                                que:"{que_re}"}}
                            )
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
    
    </script>
    </body>
    </html>"""
            else:
                page = pyadmin.login.login_again
    response = Response(body=page, content_type="text/html", charset="utf8", status="200 OK")
    return response(environment, start_response)


session_opts = pyadmin.sess.session_opts
application = SessionMiddleware(application, session_opts)
