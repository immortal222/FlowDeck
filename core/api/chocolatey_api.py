import logging
import re

import requests

logger = logging.getLogger(__name__)


class ChocolateyAPI:
    """Handles communication with the Chocolatey OData API to retrieve package metadata."""

    def __init__(self):
        self.base_url = "https://community.chocolatey.org/api/v2/Packages()"

    def search_app(self, app_name):
        """Searches for an application in Chocolatey's gallery, favoring portable versions."""
        clean_name = app_name.lower().strip().replace("+", "plus").replace(" ", "")

        # Try both common Chocolatey portable naming conventions
        for suffix in [".portable", "-portable"]:
            choco_id = f"{clean_name}{suffix}"
            url = f"{self.base_url}?$filter=Id eq '{choco_id}' and IsLatestVersion eq true"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            try:
                logger.debug(f"Searching at: {url}")
                response = requests.get(url, headers=headers, timeout=15)

                if response.status_code == 200:
                    text = response.text

                    # If a valid package entry is found, parse and return metadata
                    if "<entry" in text:
                        version_match = re.search(
                            r'<d:Version>([^<]+)</d:Version>', text)
                        desc_match = re.search(
                            r'<d:Description>([^<]+)</d:Description>', text)
                        url_match = re.search(
                            r'<d:ProjectUrl>([^<]+)</d:ProjectUrl>', text)
                        download_match = re.search(r'src="([^"]+)"', text)

                        if version_match:
                            logger.debug(f"Success! Found as: {choco_id}")
                            return {
                                "name": app_name.title(),
                                "version": version_match.group(1),
                                "description": desc_match.group(1) if desc_match else "Description not found.",
                                "homepage": url_match.group(1) if url_match else "",
                                "url": download_match.group(1) if download_match else "",
                                "source": "chocolatey"
                            }
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(
                    f"Server is down or unreachable for Chocolatey: {e}")
                return "SERVER_ERROR"
            except Exception as e:
                logger.error(f"Error while searching for {choco_id}: {e}")

        logger.debug(
            "Application not found in portable formats (.portable / -portable).")
        return None
