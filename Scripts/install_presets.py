"""
Author: Taylor B.
Project: led-matrix-battery

File: preset_installer.py

Description:
    Provides a CLI to download JSON preset files from the GitHub repository and save them locally.

Classes:
    - PresetInstaller

Functions:
    - main

Constants:
    - API_URL
    - REQ_HEADERS
    - REPO_PRESETS_URL

Dependencies:
    - typing
    - pathlib
    - requests
    - tqdm
    - inspy_logger
    - inspyre_toolbox.path_man.provision_path
    - led_matrix_battery.common.helpers.verify_checksum
    - led_matrix_battery.led_matrix.constants.PROJECT_URLS, APP_DIRS
    - led_matrix_battery.common.helpers.github_api.assemble_github_content_path_url

Example Usage:
    python -m led_matrix_battery.preset_installer \
        --app-dir /path/to/data \
        --overwrite \
        --no-progress
"""

import argparse
from typing import List, Dict, Optional, Union
from pathlib import Path

import requests
from tqdm import tqdm

from led_matrix_battery.led_matrix.constants import PROJECT_URLS, APP_DIRS
from led_matrix_battery.common.helpers import verify_checksum
from inspy_logger import InspyLogger
from inspyre_toolbox.path_man import provision_path
from led_matrix_battery.common.helpers.github_api import assemble_github_content_path_url as assemble_url

LOGGER = InspyLogger('LEDMatrixLib:PresetInstaller', console_level='debug', no_file_logging=True)

API_URL = PROJECT_URLS['github_api']
REQ_HEADERS = {"Accept": "application/vnd.github.v3+json"}
REPO_PRESETS_URL = assemble_url('presets')


class PresetInstaller:
    """
    Downloads JSON preset files from a GitHub repository and saves them locally.

    Parameters:

        url (str):
            The GitHub API URL to list preset files.

        headers (Dict[str, str]):
            HTTP headers to use for API requests.

        app_dir (Union[str, Path]):
            Local directory to save downloaded presets.

        overwrite_existing (bool):
            Whether to overwrite existing files.

        with_progress (bool):
            Whether to show progress bars.
    """

    def __init__(
        self,
        url: str = REPO_PRESETS_URL,
        headers: Optional[Dict[str, str]] = None,
        app_dir: Union[str, Path] = APP_DIRS.user_data_path,
        overwrite_existing: bool = False,
        with_progress: bool = True
    ):
        self.url = url
        self.headers = headers or REQ_HEADERS
        self.app_dir = provision_path(app_dir)
        self.overwrite = overwrite_existing
        self.with_progress = with_progress

        # ensure presets directory exists
        self.presets_dir = self.app_dir / 'presets'
        self.presets_dir.mkdir(parents=True, exist_ok=True)
        self.log = LOGGER.get_child(self.__class__.__name__)

    def run(self):
        """
        Fetches the list of files from GitHub and processes each JSON preset.
        """
        self.log.debug(f"Fetching file list from {self.url}")
        files = self.get_file_list()
        iterator = tqdm(files, desc="Processing files", unit="file") if self.with_progress else files

        for f in iterator:
            if self._is_json(f):
                self._process_file(f)
            else:
                self.log.debug(f"Skipping non-JSON file: {f.get('name')}")

    def get_file_list(self) -> List[Dict]:
        """
        Retrieves the JSON list of files from the GitHub API.

        Returns:
            List[Dict]: A list of file info dicts.
        """
        res = requests.get(self.url, headers=self.headers)
        res.raise_for_status()
        return res.json()

    def _is_json(self, file_info: Dict) -> bool:
        return file_info.get('type') == 'file' and file_info.get('name', '').endswith('.json')

    def _same_file_available_locally(self, remote_info: Dict, local_path: Path) -> bool:
        """
        Check if a file with the same name and checksum exists locally.
        """
        if not local_path.exists():
            return False
        return verify_checksum(remote_info['sha'], local_path)

    def _process_file(self, file_info: Dict):
        """
        Download and save a single JSON preset file if needed.
        """
        name = file_info['name']
        local_path = self.presets_dir / name

        if self._same_file_available_locally(file_info, local_path):
            if not self.overwrite:
                self.log.debug(f"{name} exists and matches remote; skipping.")
                return
            self.log.warning(f"{name} exists but overwrite enabled; re-downloading.")

        if self.with_progress:
            self._download_with_progress(file_info, local_path)
        else:
            self._download_simple(file_info, local_path)

        if not verify_checksum(file_info['sha'], local_path):
            self.log.error(f"Checksum mismatch for {name}")
            raise ValueError(f"Checksum verification failed for {name}")

    def _download_simple(self, file_info: Dict, local_path: Path):
        """
        Download a file without progress tracking.
        """
        res = requests.get(file_info['download_url'])
        res.raise_for_status()
        self.save_file(local_path, res.content.decode('utf-8'), overwrite=self.overwrite)

    def _download_with_progress(self, file_info: Dict, local_path: Path):
        """
        Download a file with a tqdm progress bar.
        """
        url = file_info['download_url']
        res = requests.get(url, stream=True)
        res.raise_for_status()
        total = int(res.headers.get('content-length', 0))
        bar = tqdm(total=total, unit='B', unit_scale=True, desc=f"Downloading {file_info['name']}", leave=False)

        chunks = []
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:
                chunks.append(chunk)
                bar.update(len(chunk))
        bar.close()

        content = b''.join(chunks).decode('utf-8')
        self.save_file(local_path, content, overwrite=self.overwrite)

    @staticmethod
    def save_file(path: Path, data: str, overwrite: bool = False):
        """
        Writes data to a file, optionally skipping if exists.

        Parameters:

            path (Path):
                The target file path.

            data (str):
                The text content to write.

            overwrite (bool):
                Whether to overwrite an existing file.
        """
        path = provision_path(path)
        if path.exists() and not overwrite:
            LOGGER.get_child('save_file').warning(f"Skipping existing file {path}")
            return
        with open(path, 'w') as f:
            f.write(data)
        LOGGER.get_child('save_file').debug(f"Wrote file {path}")


def main():
    """
    Command-line interface for downloading presets.
    """
    parser = argparse.ArgumentParser(description="Install JSON presets from GitHub")
    parser.add_argument(
        '--url',
        help="GitHub API URL for presets",
        default=REPO_PRESETS_URL
    )
    parser.add_argument(
        '--app-dir',
        help="Local directory to save presets",
        default=str(APP_DIRS.user_data_path)
    )
    parser.add_argument(
        '--overwrite',
        help="Overwrite existing files",
        action='store_true'
    )
    parser.add_argument(
        '--no-progress',
        help="Disable progress bars",
        action='store_false',
        dest='with_progress'
    )

    args = parser.parse_args()

    installer = PresetInstaller(
        url=args.url,
        headers=REQ_HEADERS,
        app_dir=args.app_dir,
        overwrite_existing=args.overwrite,
        with_progress=args.with_progress
    )
    installer.run()


if __name__ == '__main__':
    main()
