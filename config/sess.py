#session
import importlib
import module
importlib.reload(module)

session_opts = {
    'session.type': 'file',
    'session.cookie_expires':3000000, #True hoac 300 3000 ..v.v..v
#	'session.data_dir': './data',
	'session.data_dir': '/tmp',
#'session.domain' = '.domain.com',
'session.path' : f'{module.project}',
	'session.auto': True    
}
