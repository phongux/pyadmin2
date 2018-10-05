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
                        <div class="text-center modal-header">
                            <h4 class="text-center modal-title" style="text-align: center;" >Login</h4>
                        </div>
                        <div class="modal-body">
                        <form class="form-horizontal" role="form" action = 'login.py' method='post'>
                            <div class="form-group">
                                <label for="inputEmail1" class="col-lg-4 control-label">User name</label>
                                <div class="col-lg-5">
                                    <input type="text" class="form-control" id="inputuser1" name='username' placeholder="test" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="inputPassword1" class="col-lg-4 control-label">Password</label>
                                <div class="col-lg-5">
                                    <input type="password" class="form-control" id="inputPassword1" name='password' placeholder="123" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="g-recaptcha col-lg-offset-4 col-lg-5" data-sitekey="6LdQQmQUAAAAAIX6RkWjiN7AaswBrFw73HMlMAw4"></div>
                            </div>								
                            <!--<div class="form-group">
                                <div class="col-lg-offset-4 col-lg-5">
                                    <div class="checkbox">
                                        <label>
                                            <input type="checkbox"> Remember me
                                        </label>
                                    </div>
                                </div>
                            </div>-->
                            <div class="form-group">
                                <div class="col-lg-offset-4 col-lg-5">
                                    <button type="submit" class="btn btn-default">Sign in</button>
                                </div>
                            </div>
                            
                        </form>
                    </div>
                    <div class="modal-footer">
                    <a href='/wsgi/pyadmin/register_form'>Register</a>
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
