def application(environment, start_response):
    from webob import Request, Response
    request = Request(environment)
    params = request.params
    post = request.POST
    res = Response()
    import importlib
    import pyadmin.module
    importlib.reload(pyadmin.module)
    bootstrap = pyadmin.module.bootstrap
    js = pyadmin.module.js
	#api_url     = 'https://www.google.com/recaptcha/api/siteverify'
	#site_key    = '6LdQQmQUAAAAAIX6RkWjiN7AaswBrFw73HMlMAw4'
	#secret_key  = '6LdQQmQUAAAAAGhiipTy057aMWHnPuLkEQet8pDy'
	#url= $response = file_get_contents("https://www.google.com/recaptcha/api/siteverify?secret=6LedT9wSAAAAAHRdSVndnSjeiDtkx6hKWQ-*****&response=".$captcha."&remoteip=".$_SERVER['REMOTE_ADDR']);
    page = f"""
	<!doctype html>
		<html>
			<head>
                <title> Login </title>
                <script src="{js}/jquery.js"></script>
				<script src="{bootstrap}/js/bootstrap.js"></script>
				<link rel="stylesheet" href="{bootstrap}/css/bootstrap.css">
				<script src='https://www.google.com/recaptcha/api.js'></script>
            </head>	

		<body>

					<div class="modal-dialog">
						<div class="modal-content">
							<div class="modal-header">
							<h4 class="modal-title">Login</h4>
						</div>
						<div class="modal-body">
						<form class="form-horizontal" role="form" action = 'login.py' method='post'>
							<div class="form-group">
								<label for="inputEmail1" class="col-lg-4 control-label">User name</label>
								<div class="col-lg-5">
									<input type="text" class="form-control" id="inputuser1" name='username' placeholder="test">
								</div>
							</div>
								<div class="form-group">
									<label for="inputPassword1" class="col-lg-4 control-label">Password</label>
									<div class="col-lg-5">
										<input type="password" class="form-control" id="inputPassword1" name='password' placeholder="123">
									</div>
								</div>
							<div class="form-group">
								<div class="g-recaptcha col-lg-offset-4 col-lg-5" data-sitekey="6LdQQmQUAAAAAIX6RkWjiN7AaswBrFw73HMlMAw4"></div>
							</div>								
								<div class="form-group">
								<div class="col-lg-offset-4 col-lg-5">
									<div class="checkbox">
										<label>
											<input type="checkbox"> Remember me
										</label>
									</div>
								</div>
							</div>
							<div class="form-group">
								<div class="col-lg-offset-4 col-lg-5">
									<button type="submit" class="btn btn-default">Sign in</button>
								</div>
							</div>
							
						</form>
					</div>
					<div class="modal-footer">

					</div>
				</div><!-- /.modal-content -->
			</div><!-- /.modal-dialog -->		

		</body>
	</html>"""

    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")

    return response(environment, start_response)
