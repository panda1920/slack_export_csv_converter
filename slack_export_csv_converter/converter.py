# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from typing import cast, List, Dict, Any, Tuple

from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.file_io import FileIO
from slack_export_csv_converter.csv_data_generator import CSVDataGenerator


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

            csv_path = self._export_dir.get_csv_channel_path(channel)
            message_files = self._export_dir.get_message_files(channel)
            (csv_data_messages, csv_data_attachments) = self._gather_data(message_files)

            self._file_io.csv_write(
                csv_path / "messages.csv",
                self._csv_data_generator.get_message_fields(),
                csv_data_messages,
            )
            self._file_io.csv_write(
                csv_path / "attachments.csv",
                self._csv_data_generator.get_attachment_fields(),
                csv_data_attachments,
            )

    def _gather_data(
        self, message_files: List[Path]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        csv_data_messages = []
        csv_data_attachments = []

        for message_file in message_files:
            file_content = cast(
                List[Dict[str, Any]], self._file_io.read_json(message_file)
            )

            csv_data = self._csv_data_generator.generate_messages(file_content)
            csv_data_messages.extend(csv_data)

            csv_data = self._csv_data_generator.generate_attachments(file_content)
            csv_data_attachments.extend(csv_data)

        return (
            csv_data_messages,
            csv_data_attachments,
        )
