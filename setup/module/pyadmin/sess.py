#session
import importlib,pyadmin.module
importlib.reload(pyadmin.module)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires':3000000, #True hoac 300 3000 ..v.v..v
#	'session.data_dir': './data',
	'session.data_dir': '/tmp',
#'session.domain' = '.domain.com',
'session.path' : '%s'%pyadmin.module.project,	
	'session.auto': True    
}
