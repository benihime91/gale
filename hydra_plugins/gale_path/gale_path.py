from hydra.core.config_search_path import ConfigSearchPath
from hydra.plugins.search_path_plugin import SearchPathPlugin


class ClassyVisionPathPlugin(SearchPathPlugin):
    def manipulate_search_path(self, search_path: ConfigSearchPath) -> None:
        search_path.append(provider="gale", path="pkg://gale.hydra")
        search_path.prepend(provider="gale", path="pkg://references")
        search_path.prepend(provider="gale", path="pkg://hydra")
