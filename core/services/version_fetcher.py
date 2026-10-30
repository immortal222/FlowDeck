import logging


from core.api.scoop_api import ScoopAPI
from core.api.chocolatey_api import ChocolateyAPI

logger = logging.getLogger(__name__)


class VersionMetadataFetcher:
    """Fetches latest version metadata from supported sources.

    Returns a dict with keys: 'latest_version', 'homepage', 'source',
    'error' (optional) and 'server_error' (optional boolean).
    """

    def __init__(self):
        self.scoop = ScoopAPI()
        self.choco = ChocolateyAPI()

    def fetch(self, name, source="manual", url=""):
        import requests  # Staying here for fast startup, as requests is only used in this method
        try:
            # GitHub Releases
            if source == "github" and url:
                repo = url.replace("https://github.com/", "").strip("/")
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                resp = requests.get(api_url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    latest = data.get("tag_name")
                    return {"latest_version": latest, "homepage": None, "source": "github"}
                else:
                    return {"latest_version": None, "homepage": None, "source": "github"}

            # Chocolatey
            if source == "chocolatey":
                search_term = name.lower().replace(" ", "").replace("++", "plusplus")
                choco_data = self.choco.search_app(search_term)
                if choco_data == "SERVER_ERROR":
                    return {"server_error": True}
                if choco_data and choco_data.get("version"):
                    return {"latest_version": choco_data.get("version"), "homepage": choco_data.get("homepage"), "source": "chocolatey"}
                return {"latest_version": None, "homepage": None, "source": "chocolatey"}

            # Scoop or manual / fallback
            scoop_data = self.scoop.search_app(name)
            if scoop_data == "SERVER_ERROR":
                return {"server_error": True}
            if scoop_data and scoop_data.get("version"):
                return {"latest_version": scoop_data.get("version"), "homepage": scoop_data.get("homepage"), "source": "scoop"}
            return {"latest_version": None, "homepage": None, "source": "scoop"}

        except Exception as e:
            logger.warning(f"Version fetch failed for {name} ({source}): {e}")
            return {"latest_version": None, "homepage": None, "source": source, "error": str(e)}
