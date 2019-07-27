#Pyadmin

Pyadmin is a tool for managing content in Postgresql databases. Pyadmin is written in python, serving python scripts with apache mod_wsgi for managing content in Postgresql databases. System Requirements: (all newest version install on FreeBSD OS is recommended). Web service: Apache. Database : Postgresql. Python module:

 +   Modwsgi
  +  Psycopg2
   + Webob
    +beaker ... 
    
    +Useful resources: http://koo.fi/blog/2012/12/02/serving-python-scripts-with-apache-mod_wsgi-part-i/

+https://www.youtube.com/watch?v=HWpctdhd2W4

+http://simplepypgadmin.blogspot.com/2017/07/
# pyadmin2

Some point :
#2 line below to set pyadmin2 as document root when run in fact with apache and modwsgi
import sys
sys.path.insert(0,"E:\Projects\pyadmin2")
###
if you debug in pycharm do not need 2 line below

* We have file httpd.conf example for win and ubuntu in pyadmin2\setup\apache_config\apache_window, pyadmin2\setup\apache_config\apache_ubuntu folder
* In future, we will make a video how to configure apache with mod_wsgi on window if we have free time.
* We sorry about less document, so in the future if we have more free time , we will make document completly.