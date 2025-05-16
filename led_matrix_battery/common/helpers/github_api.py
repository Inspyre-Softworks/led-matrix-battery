"""


Author: 
    Inspyre Softworks

Project:
    led-matrix-battery

File: 
    led_matrix_battery/common/helpers/github_api.py
 

Description:
    

"""
from led_matrix_battery.led_matrix.constants import PROJECT_URLS, GITHUB_URL_SUFFIX


def assemble_github_content_path_url(
        relative_path: str,  # e.g. 'dev_tools/presets.py'
        branch:        str = 'master',
        base_url:      str = PROJECT_URLS['github_api']
):
    """
    Assemble a GitHub content path URL.

    Parameters:
        relative_path (str):
            The relative path to the file in the GitHub repository.
        branch (str, optional):
            The branch name. Defaults to 'master'.
        base_url (str, optional):
            The base URL of the GitHub API. Defaults to PROJECT_URLS['github_api'].
        suffix (str, optional):
            The URL suffix. Defaults to GITHUB_URL_SUFFIX.

    Returns:
        str:
            The assembled GitHub content path URL.
    """
    return f"{base_url}/{relative_path}?ref={branch}"
