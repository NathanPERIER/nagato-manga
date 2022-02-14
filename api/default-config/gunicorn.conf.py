
import os
import json

# More information on this configuration file here : https://docs.gunicorn.org/en/stable/settings.html#settings

loglevel = 'info'

proc_name = 'nagato-api'

# More than one worker ruins the caching done by the API
# In order to solve this, we should use an external service like Redis
# but this would probably be overkill
threads = 1
workers = 1

nagato_host = os.getenv('NAGATO_HOST') if 'NAGATO_HOST' in os.environ else '0.0.0.0'
nagato_port = os.getenv('NAGATO_PORT') if 'NAGATO_PORT' in os.environ else '8090'
bind = [f"{nagato_host}:{nagato_port}"]


def _deepMerge(d1: dict, d2: dict) :
	for k, v in d2.items() :
		if k in d1 and isinstance(v, dict) and isinstance(d1[k], dict) :
			_deepMerge(d1[k], v)
		else :
			d1[k] = d2[k]

def _completeConf(default_path, true_path) :
	with open(default_path, 'r') as f :
		default_conf = json.load(f)
	do_save = True
	if os.path.exists(true_path) :
		with open(true_path, 'r') as f :
			user_conf = json.load(f)
		# Apply the user-defined configuration above the default configuration
		_deepMerge(default_conf, user_conf)
		do_save = default_conf != user_conf
	if do_save :
		with open(true_path, 'w') as f :
			return json.dump(default_conf, f, indent='\t')

# Called each time the servr is started
def on_starting(_server):
	this_dir = os.path.realpath(os.path.dirname(__file__))
	conf_dir = os.path.join(os.path.dirname(this_dir), 'config')
	if not os.path.exists(conf_dir) :
		os.mkdir(conf_dir)
	for filename in ['conf.json', 'env.json'] :
		_completeConf(os.path.join(this_dir, filename), os.path.join(conf_dir, filename))


# Alternate solution found on StackOverflow
# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries/7205107#7205107
# def merge(a, b, path=None):
#     "merges b into a"
#     if path is None: path = []
#     for key in b:
#         if key in a:
#             if isinstance(a[key], dict) and isinstance(b[key], dict):
#                 merge(a[key], b[key], path + [str(key)])
#             elif a[key] == b[key]:
#                 pass # same leaf value
#             else:
#                 raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
#         else:
#             a[key] = b[key]
#     return a
