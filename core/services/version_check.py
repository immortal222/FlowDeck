import requests
from packaging.version import parse as parse_version


def check_github_updates(username="immortal222", repo="FlowDeck", current_version="0.1.0"):
    """
    Checks the GitHub API for the latest release.

    :param username: str - Your GitHub username or organization
    :param repo: str - The name of the repository 
    :param current_version: str - The current version of the application 
    """
    url = f"https://api.github.com/repos/{username}/{repo}/releases/latest"

    # It's good practice to include a User-Agent header in requests to the GitHub API
    headers = {'User-Agent': 'Python-Update-Checker'}

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            # The GitHub API returns the version in the "tag_name" field (e.g., "v1.2.0" or "1.2.0")
            remote_tag = data.get("tag_name")

            # We remove the 'v' prefix if it exists (e.g., "v1.2.0" -> "1.2.0")
            latest_version = remote_tag.lstrip('v')

            # Version comparison
            if parse_version(latest_version) > parse_version(current_version):
                update_info = {
                    "version": latest_version,
                    # The title of the Release
                    "title": data.get("name"),
                    # The changelog for the Release
                    "changelog": data.get("body"),
                    # The link to the Release page
                    "html_url": data.get("html_url")
                }
                print(
                    f"Update available: {latest_version} (Current: {current_version})")
                return True, update_info
            else:
                return False, None

        elif response.status_code == 404:
            print("The repository was not found or has no releases yet.")
            return False, None
        else:
            print(f"Error with GitHub API: HTTP {response.status_code}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return False, None
