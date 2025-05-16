import hashlib
from pathlib import Path
from led_matrix_battery.led_matrix.constants import PROJECT_URLS
import requests
from inspyre_toolbox.path_man import provision_path



def download_presets():
    url = PROJECT_URLS['github_api']



def calculate_checksum(file_path):
    """
    Calculate the SHA-256 checksum of a file.

    Parameters:
        file_path (Union[str, Path]):
            The path to the file for which to calculate the checksum.

    Returns:
        str:
            The SHA-256 checksum of the file.
    """
    if not isinstance(file_path, Path):
        file_path = provision_path(file_path)

    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)

    return sha256.hexdigest()



def percentage_to_value(percent, max_value=255):
    """
    Convert a percentage value to an actual value between 0 and `max_value`.

    Parameters:
        percent (float):
            The percentage value to convert.

        max_value (int, optional):
            The maximum value to which the percentage should be converted. Defaults to 255.

    Returns:
        int:
            The converted value between 0 and `max_value`.
    """
    if not isinstance(percent, (int, float)):
        raise TypeError(f'percent must be of type int or float, not {type(percent)}')

    if percent < 0 or percent > 100:
        raise ValueError(f'percent must be between 0 and 100, not {percent}')

    return int(round(percent * max_value / 100))


def verify_checksum(remote_checksum, local_file_path):
    """
    Verify the checksum of a local file against a remote checksum.

    Parameters:
        remote_checksum (str):
            The remote checksum to verify against.

        local_file_path (Union[str, Path]):
            The path to the local file to verify.

    Returns:
        bool:
            True if the checksums match, False otherwise.
    """
    if not isinstance(local_file_path, Path):
        local_file_path = provision_path(local_file_path)

    sha256 = hashlib.sha256()

    with open(local_file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)

    local_checksum = sha256.hexdigest()

    return local_checksum == remote_checksum


def download_file(url, local_path, headers=None):
    """
    Download a file from a URL and save it to a local path.

    Parameters:
        url (str):
            The URL of the file to download.

        local_path (Union[str, Path]):
            The local path to save the downloaded file.

        headers (Optional[Dict]):
            The headers to use for the request. Defaults to None.
    """
    if not isinstance(local_path, Path):
        local_path = provision_path(local_path)

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

