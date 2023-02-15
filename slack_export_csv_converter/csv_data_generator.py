# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Any, Union, Optional
from datetime import datetime
import re
import urllib.parse

import logging


class CSVDataGenerator:
    """
    This class is responsible for generating csv data from exported slack message files.
    Knowledge of how to parse/interpret the export files is localized in this class to
    promote decoupling.
    """

    def __init__(self, users_data: List[Dict[str, Any]]) -> None:
        self._userid_name_mapping = {user["id"]: user["name"] for user in users_data}

    def generate_messages(
        self, messages_data: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, str]]]:
        """Generates csv data from messages file

        Args:
            messages_data: data retrieved from messages file

        Returns:
            Tuple of fields and data
        """
        # logging.warning(str(messages-data))
        generated_messages = []
        fields = [
            "ts",
            "投稿日時",
            "ユーザー",
            "テキスト",
            "thread_ts",
        ]

        for message in messages_data:
            if not message["type"] == "message":
                continue

            generated_message = {
                field: self._convert_field(field, message) for field in fields
            }

            generated_messages.append(generated_message)

        return (fields, generated_messages)

    def generate_attachments(
        self, messages_data: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[Dict[str, str]]]:
        generated_attachments = []
        fields = ["file_ts", "アップロード日時", "ユーザー", "message_ts", "url", "ファイル名"]

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

        return (fields, generated_attachments)

    def _convert_field(
        self,
        field_name: str,
        message: Dict[str, Any],
        attachment: Optional[Dict[str, Any]] = None,
    ) -> str:
        if field_name == "ts":
            field_value = message["ts"]
        elif field_name == "投稿日時":
            field_value = self._convert_ts(message["ts"])
        elif field_name == "ユーザー":
            field_value = self._convert_userid(message["user"])
        elif field_name == "テキスト":
            field_value = message["text"]
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

    def _convert_filename(self, attachment: Dict[str, Any]) -> str:
        date = re.sub("[- :]", "", self._convert_ts(attachment["created"]))
        name = attachment.get("name")
        if not name:
            path = urllib.parse.urlparse(attachment["url_private"]).path
            name = path[path.rfind("/") + 1 :]
        return f"{date}_{name}"
