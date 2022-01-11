from nagato.downloaders.base import BaseDownloader
import logging
import pkgutil
import validators

logger = logging.getLogger(__name__)

custom_downloaders = {}

def register(site) :
	def decorator(dl_class) :
		if site is None or not validators.url(f"https://{site}") :
			raise ValueError(f"Incorrect site name for downloader {dl_class.__name__} : \"{site}\"")
		if not issubclass(dl_class, BaseDownloader) : 
			raise ValueError(f"Class {dl_class.__name__} does not inherit {BaseDownloader.__name__}")
		if site in custom_downloaders :
			logger.warning(f"downloader {dl_class.__name__} for site \"{site}\" will overshadow downloader {custom_downloaders[site].__name__}")
		else :
			logger.info(f"found downloader {dl_class.__name__} for site \"{site}\"")
		custom_downloaders[site] = dl_class
		return dl_class
	return decorator


def load_submodules() :
	# __all__ = []
	for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
		# logger.info(f"Found module {module_name}")
		# __all__.append(module_name)
        # _module =
		loader.find_module(module_name).load_module(module_name)
		# globals()[module_name] = _module
