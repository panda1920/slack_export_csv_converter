# -*- coding: utf-8 -*-
from pathlib import Path
from typing import List, Optional

from slack_export_csv_converter.exceptions import ConverterException


class ExportDir:
    """
    A class that abstracts away directory structure of slack exports.
    The motivation is to free the burden of consumers of this class from worrying about
    how the exported files are laid out and where it is located.
    """

    _USERS_FILE_NAME = "users.json"

    def __init__(self, export_dir: Path, csv_path: Path):
        self._check_exists(export_dir)
        self._export_dir = export_dir
        self._csv_path = csv_path
        self._channel_paths = [
            dir.stem for dir in self._export_dir.iterdir() if dir.is_dir()
        ]

    def get_users_file(self) -> Path:
        """Get path to a file containing user information from within slack export

        Returns:
            Path to a json file containing user information
        """
        users_file = self._export_dir / self._USERS_FILE_NAME
        self._check_exists(users_file)

        return users_file

    def get_channels(self) -> List[str]:
        """Get all existing channel in the export

        Returns:
            List of channel names
        """
        return self._channel_paths

    def get_message_files(self, channel: str) -> List[Path]:
        """Get paths to all message files belonging to a channel

        Args:
            channel: name of channel

        Returns:
            path to message json files
        """
        channel_path = self._export_dir / channel
        self._check_exists(channel_path, f"チャンネル名 {channel} は存在しません")
        return [
            file
            for file in channel_path.iterdir()
            if file.is_file() and file.suffix == ".json"
        ]

    def _check_exists(self, path: Path, fail_msg: Optional[str] = None) -> None:
        if fail_msg is None:
            fail_msg = f"{str(path)} が見つかりません"

        if not path.exists():
            raise ConverterException(fail_msg)

    def get_csv_channel_path(self, channel: str) -> Path:
        """Retrieve path to store csv converted data of specified channel.

        In the process a new folder is created if not found.

        Args:
            channel: name of slack channel

        Returns:
            path to store store csv converted data of channel specified by "channel"
        """
        if channel not in self._channel_paths:
            raise ConverterException(f"チャンネル名 {channel} は存在しません")

        csv_channel_path = self._csv_path / channel
        csv_channel_path.mkdir(parents=True, exist_ok=True)
        return csv_channel_path

    def get_attachments_path(self, channel: str) -> Path:
        """Retreive path to store attachment files found in specified channel.

        In the process a new folder is created if not found.

        Args:
            channel: name of slack channel

        Returns:
            path to store attachments file
        """
        if channel not in self._channel_paths:
            raise ConverterException(f"チャンネル名 {channel} は存在しません")

        attachments_path = self._csv_path / channel / "attachments"
        attachments_path.mkdir(parents=True, exist_ok=True)
        return attachments_path
