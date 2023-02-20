# -*- coding: utf-8 -*-
from typing import Union, Optional
from datetime import datetime
from re import sub, compile, Match
import urllib.parse

from .types import ExportFileContent, ExportFileElement, CSVData, CSVFields


class CSVDataGenerator:
    """
    This class is responsible for generating csv data from exported slack message files.
    Knowledge of how to parse/interpret the export files is localized in this class to
    promote decoupling.
    """

    def __init__(self, users_data: ExportFileContent) -> None:
        self._userid_name_mapping = {
            user["id"]: user["profile"]["real_name"] for user in users_data
        }

    def get_message_fields(self) -> CSVFields:
        """Get list of fields message csv file should have

        Returns:
            List of fields
        """
        return ["ts", "投稿日時", "ユーザー", "テキスト", "thread_ts"]

    def generate_messages(self, messages_data: ExportFileContent) -> CSVData:
        """Generates csv data from messages file

        Args:
            messages_data: data retrieved from messages file

        Returns:
            Tuple of fields and data
        """
        # logging.warning(str(messages-data))
        generated_messages = []
        fields = self.get_message_fields()

        for message in messages_data:
            if not message["type"] == "message":
                continue

            generated_message = {
                field: self._convert_field(field, message) for field in fields
            }

            generated_messages.append(generated_message)

        return generated_messages

    def get_attachment_fields(self) -> CSVFields:
        """Get list of fields attachment csv file should have

        Returns:
            List of fields
        """
        return ["file_ts", "アップロード日時", "ユーザー", "message_ts", "url", "ファイル名"]

    def generate_attachments(self, messages_data: ExportFileContent) -> CSVData:
        generated_attachments = []
        fields = self.get_attachment_fields()

        for message in messages_data:
            files = message.get("files")
            if not files:
                continue

            for attachment in files:
                if not attachment.get("url_private"):
                    continue

                generated_attachment = {
                    field: self._convert_field(field, message, attachment)
                    for field in fields
                }

                generated_attachments.append(generated_attachment)

        return generated_attachments

    def _convert_field(
        self,
        field_name: str,
        message: ExportFileElement,
        attachment: Optional[ExportFileElement] = None,
    ) -> str:
        if field_name == "ts":
            field_value = message["ts"]
        elif field_name == "投稿日時":
            field_value = self._convert_ts(message["ts"])
        elif field_name == "ユーザー":
            field_value = self._convert_userid(message.get("user", ""))
        elif field_name == "テキスト":
            field_value = self._convert_textcontent(message["text"])
        elif field_name == "thread_ts":
            field_value = message.get("thread_ts", "")
        elif field_name == "file_ts" and attachment is not None:
            field_value = str(attachment["created"])
        elif field_name == "アップロード日時" and attachment is not None:
            field_value = self._convert_ts(attachment["created"])
        elif field_name == "message_ts":
            field_value = message["ts"]
        elif field_name == "url" and attachment is not None:
            field_value = attachment["url_private"]
        elif field_name == "ファイル名" and attachment is not None:
            field_value = self._convert_filename(attachment)
        else:
            field_value = ""

        return field_value

    # conversion methods
    @staticmethod
    def _convert_ts(ts: Union[str, int]) -> str:
        return str(datetime.fromtimestamp(float(ts)))

    def _convert_userid(self, userid: str) -> str:
        return self._userid_name_mapping.get(userid, "Not available")

    def _convert_filename(self, attachment: ExportFileElement) -> str:
        date = sub("[- :]", "", self._convert_ts(attachment["created"]))
        name = attachment.get("name")
        if not name:
            path = urllib.parse.urlparse(attachment["url_private"]).path
            name = path[path.rfind("/") + 1 :]
        return f"{date}_{name}"

    def _convert_textcontent(self, text: str) -> str:
        return self._escape_newlines(self._convert_user_mentions(text))

    def _convert_user_mentions(self, text: str) -> str:
        mention_pattern = compile("<@(.*?)>")

        def convert_match_to_username(match: Match) -> str:
            return f"@{self._convert_userid(match.group(1))}"

        return sub(mention_pattern, convert_match_to_username, text)

    @staticmethod
    def _escape_newlines(text: str) -> str:
        return text.replace("\n", "\\n")
