# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import cast, List, Tuple

from .export_dir import ExportDir
from .file_io import FileIO
from .csv_data_generator import CSVDataGenerator
from .types import CSVData, ExportFileContent


class Converter:
    """
    Class that performs conversion of slack export files.
    """

    def __init__(
        self, export_dir: ExportDir, file_io: FileIO, csv_data_generator: CSVDataGenerator
    ) -> None:
        self._export_dir = export_dir
        self._file_io = file_io
        self._csv_data_generator = csv_data_generator

    def run(self) -> None:
        """Starts the conversion process of the slack export files.

        Does the following things:
        - Converts json message files to csv
        - Gathers attachment file info to a separate csv

        Returns:
            None
        """
        logging.info("Slackエクスポートの変換処理を開始します...")

        channels = self._export_dir.get_channels()

        for channel in channels:
            logging.info(f"チャンネル #{str(channel)} を変換中...")

            message_files = self._export_dir.get_message_files(channel)
            (csv_data_messages, csv_data_attachments) = self._gather_data(message_files)

            self._write_csv_data(csv_data_messages, csv_data_attachments, channel)
            self._download_attachments(csv_data_attachments, channel)

        logging.info("Slackエクスポートの変換処理が完了しました！")

    def _gather_data(self, message_files: List[Path]) -> Tuple[CSVData, CSVData]:
        csv_data_messages = []
        csv_data_attachments = []

        for message_file in message_files:
            file_content = cast(ExportFileContent, self._file_io.read_json(message_file))

            csv_data = self._csv_data_generator.generate_messages(file_content)
            csv_data_messages.extend(csv_data)

            csv_data = self._csv_data_generator.generate_attachments(file_content)
            csv_data_attachments.extend(csv_data)

        return (csv_data_messages, csv_data_attachments)

    def _write_csv_data(
        self, csv_data_messages: CSVData, csv_data_attachments: CSVData, channel: str
    ) -> None:
        save_location = self._export_dir.get_csv_channel_path(channel)

        self._file_io.csv_write(
            save_location / "messages.csv",
            self._csv_data_generator.get_message_fields(),
            csv_data_messages,
        )
        self._file_io.csv_write(
            save_location / "attachments.csv",
            self._csv_data_generator.get_attachment_fields(),
            csv_data_attachments,
        )

    def _download_attachments(self, csv_data_attachments: CSVData, channel: str) -> None:
        save_location = self._export_dir.get_attachments_path(channel)

        for attachment in csv_data_attachments:
            url = attachment["url"]
            file_path = save_location / attachment["ファイル名"]

            try:
                self._file_io.download(url, file_path)
            except Exception:
                # even if download fails just continue with rest of downloads
                continue
