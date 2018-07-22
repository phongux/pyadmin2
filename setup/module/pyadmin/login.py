import importlib,pyadmin.module
importlib.reload(pyadmin.module)

data = "%s/login_form"%pyadmin.module.project
again = "%s/login_form_again"%pyadmin.module.project
loginform = """<!doctype html>
		<html>
			<head>
			<meta http-equiv="refresh" content="0; url=%s"/>
                <title> redirect login </title>
            </head>	
		<body>
		</body>
	</html>"""%data

login_again = """<!doctype html>
		<html>
			<head>
			<meta http-equiv="refresh" content="0; url=%s"/>
                <title> redirect login </title>
            </head>	
		<body>
		</body>
	</html>"""%again
