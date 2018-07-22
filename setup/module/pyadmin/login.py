import importlib,pyadmin.module
importlib.reload(pyadmin.module)

data = f"{pyadmin.module.project}/login_form"
again = f"{pyadmin.module.project}/login_form_again"
loginform = f"""<!doctype html>
		<html>
			<head>
			<meta http-equiv="refresh" content="0; url={data}"/>
                <title> redirect login </title>
            </head>	
		<body>
		</body>
	</html>"""

login_again = f"""<!doctype html>
		<html>
			<head>
			<meta http-equiv="refresh" content="0; url={again}"/>
                <title> redirect login </title>
            </head>	
		<body>
		</body>
	</html>"""
