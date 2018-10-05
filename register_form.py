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
                <title> Register </title>
                <script src="{js}/jquery.js"></script>
                <script src="{bootstrap}/js/bootstrap.js"></script>
                <link rel="stylesheet" href="{bootstrap}/css/bootstrap.css">
                <script src='https://www.google.com/recaptcha/api.js'></script>
            </head>	
            <body>
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="text-center modal-header">
                            <h4 class="text-center modal-title" style="text-align: center;" >Register</h4>
                        </div>
                        <div class="modal-body">
                        <form class="form-horizontal" role="form" action = 'register.py' method='post'>
                            <div class="form-group">
                                <label for="inputFullname1" class="col-lg-6 control-label">Full name</label>
                                <div class="col-lg-5">
                                    <input type="text" class="form-control" id="inputFullname1" name='fullname' placeholder="test" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="inputUser1" class="col-lg-6 control-label">User name</label>
                                <div class="col-lg-5">
                                    <input type="text" class="form-control" id="inputUser1" name='username' placeholder="test" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="inputEmail" class="col-lg-6 control-label">Email</label>
                                <div class="col-lg-5">
                                    <input type="email" class="form-control" id="inputEmail" name='email' placeholder="" required>
                                </div>
                            </div>
                            <div class="form-group">
                            <fieldset data-role="controlgroup">
                                <legend>Choose your gender:</legend>
                                <label for="male">Male</label>
                                <input type="radio" name="gender" id="male" value="male" checked>
                                <label for="female">Female</label>
                                <input type="radio" name="gender" id="female" value="female">
                            </fieldset>

                            </div>
                            <div class="form-group">
                                <label for="inputBirthday" class="col-lg-6 control-label">Date of birth</label>
                                <div class="col-lg-5">
                                    <input type="date" class="form-control" id="inputBirthday" name='birthday' placeholder="" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="inputClass" class="col-lg-6 control-label">Department (Class)</label>
                                <div class="col-lg-5">
                                    <input type="text" class="form-control" id="inputClass" name='depart' placeholder="" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="inputSchool" class="col-lg-6 control-label">Company (School)</label>
                                <div class="col-lg-5">
                                    <input type="text" class="form-control" id="inputSchool" name='company' placeholder="" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="password" class="col-lg-6 control-label">Password</label>
                                <div class="col-lg-5">
                                    <input type="password" class="form-control" id="password" name='password' placeholder="" required>
                                </div>
                            </div>  
                            <div class="form-group">
                                <label for="confirm_password" class="col-lg-6 control-label">Confirm password</label>
                                <div class="col-lg-5">
                                    <input type="password" class="form-control" id="confirm_password" name='password' placeholder="" required>
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
                                    <button type="submit" class="btn btn-default">Sign up</button>
                                </div>
                            </div>
                            
                        </form>
                    </div>
                    <div class="modal-footer">
                    </div>
                </div><!-- /.modal-content -->
            </div><!-- /.modal-dialog -->	
            <script>
            var password = document.getElementById("password")
  , confirm_password = document.getElementById("confirm_password");

    function validatePassword(){{
      if(password.value != confirm_password.value) {{
        confirm_password.setCustomValidity("Passwords Don't Match");
      }} else {{
        confirm_password.setCustomValidity('');
      }}
    }}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;
            </script>	
            </body>
        </html>"""
    response = Response(body=page,
                        content_type="text/html",
                        charset="utf8",
                        status="200 OK")
    return response(environment, start_response)
