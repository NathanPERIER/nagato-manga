import os
import json

__this_dir = os.path.dirname(os.path.realpath(__file__))
__conf_dir = os.path.join(os.path.dirname(os.path.dirname(__this_dir)), 'config')
__conf_file = os.path.join(__conf_dir, 'conf.json')
__env_conf_file = os.path.join(__conf_dir, 'env.json')

with open(__conf_file, 'r') as f :
	conf = json.load(f)

with open(__env_conf_file, 'r') as f :
	env_conf = json.load(f)


def _transformOnAssign(d, key, new_val) :
	if key in d :
		old_val = key[d]
		if type(old_val) != str :
			d[key] = json.loads(new_val)
			return
	d[key] = new_val

def _loadEnvIfPossible(conf, env_conf, conf_name) :
	res = conf[conf_name]
	if conf_name in env_conf :
		for k, e in env_conf[conf_name].items() :
			if e in os.environ :
				_transformOnAssign(res, k, os.getenv(e))
	return res


__global_conf = _loadEnvIfPossible(conf, env_conf, 'global')

__api_conf = _loadEnvIfPossible(conf, env_conf, 'api')

__downloaders_conf = {site: _loadEnvIfPossible(conf['downloaders'], env_conf['downloaders'], site) for site in conf['downloaders']}


def getApiConf(key) :
	return __api_conf[key]

def getDownloaderConf(site) :
	if site in __downloaders_conf :
		return {**__global_conf, **__downloaders_conf[site]}
	return __global_conf
