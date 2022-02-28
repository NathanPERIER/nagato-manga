import os
import json

from nagato.utils.errors import ApiConfigurationError

__this_dir = os.path.dirname(os.path.realpath(__file__))
API_DIR = os.path.dirname(os.path.dirname(__this_dir))

__conf_dir = os.path.join(API_DIR, 'config')
__conf_file = os.path.join(__conf_dir, 'conf.json')
__env_conf_file = os.path.join(__conf_dir, 'env.json')

with open(__conf_file, 'r') as f :
	conf = json.load(f)

with open(__env_conf_file, 'r') as f :
	env_conf = json.load(f)


def _transformOnAssign(d, key, new_val) :
	if key in d :
		old_val = d[key]
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


_global_conf = _loadEnvIfPossible(conf, env_conf, 'global')

_api_conf = _loadEnvIfPossible(conf, env_conf, 'api')

_downloaders_conf = {site: _loadEnvIfPossible(conf['downloaders'], env_conf['downloaders'], site) for site in conf['downloaders']}


class DownloaderConf :

	def __init__(self, site) :
		if site in _downloaders_conf :
			self._conf = {**_global_conf, **_downloaders_conf[site]}
		else :
			self._conf = _global_conf
		self._site = site
	
	def forSite(site) -> "DownloaderConf" :
		return DownloaderConf(site)

	def __getitem__(self, key: str) -> str :
		if key in self._conf :
			return self._conf[key]
		raise ApiConfigurationError(f"Missing property \"{key}\" for the configuration of site {self._site}")
	
	def __contains__(self, key: str) -> bool :
		return key in self._conf


def getApiConf(key) :
	if key in _api_conf :
		return _api_conf[key]
	raise ApiConfigurationError(f"Missing property \"{key}\" for the configuration of the API")
