import requests

from led_matrix_battery.led_matrix.constants import PROJECT_URLS


API_URL = PROJECT_URLS['github_api']

REQ_HEADERS = {
    "Accept": "application./vnd.github.v3+json"
}


def get_file_list(url=API_URL, headers=None):
    # Set the headers if not provided:
    if headers is None:
        headers = REQ_HEADERS

    res = requests.get(url, headers=headers)

    # Check for error code:
    res.raise_for_status()

    # Return the file list:
    return res.json()


def download_grid_designs(url=API_URL, headers=REQ_HEADERS, app_dir=):
    files = get_file_list(url, headers)
    for file in files:
        if file['type'] == 'file':
            dl_url =file['download_url']


