from typing import List, Dict, Optional, Union
from pathlib import Path
import argparse
import requests

from tqdm import tqdm

from led_matrix_battery.led_matrix.constants import PROJECT_URLS, APP_DIRS
from led_matrix_battery.common.helpers import verify_checksum
from inspy_logger import InspyLogger
from inspyre_toolbox.path_man import provision_path
from led_matrix_battery.common.helpers.github_api import assemble_github_content_path_url as assemble_url

LOGGER = InspyLogger('LEDMatrixLib:PresetInstaller', console_level='debug', no_file_logging=True)


API_URL = PROJECT_URLS['github_api']

REQ_HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

REPO_PRESETS_URL          = assemble_url('presets')
REPO_PRESETS_MANIFEST_URL = assemble_url('presets/manifest.json')


def same_file_available_locally(remote_file_info: Dict, local_file_path: Path):
    """
    Check if a file with the same name and checksum is available locally.

    Parameters:
        remote_file_info (Dict):
            The remote file information containing the name and checksum.
        local_file_path (Path):
            The path to the local file to check.

    Returns:
        bool:
            True if a file with the same name and checksum is available locally, False otherwise.
    """
    log = LOGGER.get_child('same_file_available_locally')
    log.debug(f'Checking if {local_file_path} exists and matches remote file info.')

    # Check if the local file exists:
    if not local_file_path.exists():
        log.debug(f'File {local_file_path} does not exist.')
        return False

    # Verify the checksum of the local file:
    return verify_checksum(remote_file_info['sha'], local_file_path)


def get_file_list(url: str = None, headers: Optional[Dict] = None) -> List[Dict]:
    log = LOGGER.get_child('get_file_list')

    # Set the headers if not provided:
    if headers is None:
        log.debug('No headers provided, using default headers.')
        headers = REQ_HEADERS

    # Set the URL if not provided:
    if url is None:
        log.debug('No URL provided, using default URL.')
        url = API_URL

    log.debug(f'Fetching file list from {url}...')
    res = requests.get(url, headers=headers)

    # Check for error code:
    res.raise_for_status()
    files = res.json()
    log.debug(f'File list fetched successfully from {url}. | Total files: {len(files)}')

    # Return the file list:
    return files


def process_json_file(file: Dict, app_dir: Path, overwrite_existing: bool, with_prog_bars: bool = True):
    """
    Process a single JSON file from the repository.

    Parameters:
        file (Dict): The file information from the repository.
        app_dir (Path): The directory to save the file to.
        overwrite_existing (bool): Whether to overwrite existing files.
        with_prog_bars (bool): Whether to use tqdm to track download progress.
    """
    log = LOGGER.get_child('process_json_file')
    log.debug(f'Found valid JSON file: {file["name"]}')

    if not isinstance(app_dir, Path):
        app_dir = provision_path(app_dir)

    local_path = app_dir / file['name']

    # Skip if file exists locally and we're not overwriting
    if same_file_available_locally(file, local_path):
        log.debug(f'File {file["name"]} already exists and matches remote file. Skipping download.')
        if not overwrite_existing:
            return
        log.warning(f'Overwriting existing file {file["name"]}')

    # Download and save the file
    dl_url = file['download_url']
    log.debug(f'Downloading file from {dl_url}...')

    if with_prog_bars:
        __download_with_progress(file, local_path, overwrite_existing)
    else:
        __download_json_file(file, local_path, overwrite_existing, log)

    if not verify_checksum(file['sha'], local_path):
        log.error(f'Checksum verification failed for {file["name"]}.')
        raise ValueError(f'Checksum verification failed for {file["name"]}.')


def __download_json_file(file: Dict, local_path: Path, overwrite_existing: bool, log):
    dl_url = file['download_url']
    # Regular download without progress tracking
    json_data = requests.get(dl_url)
    log.debug(f'Downloaded file: {file["name"]} | Status code: {json_data.status_code}')
    json_data.raise_for_status()
    # Save the file to the app directory:
    save_file(local_path, json_data.content.decode('utf-8'), overwrite_existing)


def __download_with_progress(file_info, local_path, overwrite_existing):
    """
    Download a file with a progress bar.
    
    Parameters:
        file_info (Dict):
            The file information from the repository.
            
        local_path (Path):
            The path to save the file to.
            
        overwrite_existing (bool):
            Whether to overwrite existing files.

    Returns:
        None
        
    Raises:
        requests.exceptions.HTTPError:
            If the download fails.
            
    See Also:
        save_file
    """
    dl_url = file_info['download_url']
    # Stream with tqdm progress bar
    response = requests.get(dl_url, stream=True)
    response.raise_for_status()
    # Get file size if available
    total_size = int(response.headers.get('content-length', 0))
    # Initialize tqdm progress bar
    progress_bar = tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc=f"Downloading {file_info['name']}",
        leave=False
    )

    # Download with progress tracking
    content = b''
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            content += chunk
            progress_bar.update(len(chunk))
    progress_bar.close()

    # Save the file to the app directory
    save_file(local_path, content.decode('utf-8'), overwrite_existing)


def is_json_file(file: Dict) -> bool:
    """
    Check if a file is a JSON file.

    Parameters:
        file (Dict):
            The file information from the repository.

    Returns:
        bool:
            True if the file is a JSON file, False otherwise.
    """
    return file['type'] == 'file' and file['name'].endswith('.json')


def download_grid_designs(
        url:                Optional[str]              = None,
        headers:            Optional[Dict]             = None,
        app_dir:            Optional[Union[str, Path]] = None,
        overwrite_existing: Optional[bool]             = False,
        with_prog_bars:     Optional[bool]             = True
):
    """
    Download grid designs from a GitHub repository.
    
    Parameters:
        url (Optional[str]):
            The URL of the GitHub repository to download from. Defaults to the API URL.
            
        headers (Optional[Dict]):
            The headers to use for the request. Defaults to the API headers.
            
        app_dir (Optional[Union[str, Path]):
            The directory to save the downloaded files to. Defaults to the app directory.
            
        overwrite_existing (Optional[bool]):
            Whether to overwrite existing files. Defaults to False.
            
        with_prog_bars (Optional[bool]):
            Whether to use tqdm to track download progress. Defaults to True.

    Returns:

    """
    log = LOGGER.get_child('download_grid_designs')

    manifest_url = REPO_PRESETS_MANIFEST_URL

    if not url:
        url = REPO_PRESETS_URL

    if not headers:
        headers = REQ_HEADERS

    if not app_dir:
        app_dir = APP_DIRS.user_data_path

    if not isinstance(app_dir, Path):
        app_dir = provision_path(app_dir)

    presets_dir = app_dir.joinpath('presets')

    if not presets_dir.exists():
        log.debug(f'Creating presets directory: {presets_dir}')
        presets_dir.mkdir(parents=True, exist_ok=True)

    files = get_file_list(url, headers)
    log.debug(f'Found {len(files)} files in the repository.')

    # Process each file
    file_iterator = files
    if with_prog_bars:
        file_iterator = tqdm(files, desc="Processing files", unit="file")

    for file in file_iterator:
        if is_json_file(file):
            process_json_file(file, presets_dir, overwrite_existing, with_prog_bars)
        elif file['type'] == 'file' and not file['name'].endswith('json'):
            log.debug(f'Skipping non-JSON file: {file["name"]}')
        elif file.get('dir', False):
            log.debug(f'Skipping directory: {file["name"]}')

        local_fp = presets_dir.joinpath(file['name'])


def save_file(file_path: Path, data, overwrite: bool = False):
    log = LOGGER.get_child('save_file')
    file_path = provision_path(file_path)

    # Check if the file already exists:
    if file_path.exists() and not overwrite:
        log.warning(f'File {file_path} already exists. Skipping download.')
        return

    # Save the file:
    with open(file_path, 'w') as f:
        f.write(data)
        log.debug(f'Saved file: {file_path}')


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install LED matrix grid presets")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing preset files if they already exist",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bars during download",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    args = build_arg_parser().parse_args(argv)

    download_grid_designs(
        overwrite_existing=args.overwrite,
        with_prog_bars=not args.no_progress,
    )


if __name__ == "__main__":
    main()


