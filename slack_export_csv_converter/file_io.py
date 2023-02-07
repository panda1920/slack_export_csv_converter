# -*- coding: utf-8 -*-
import json
from csv import DictWriter, QUOTE_ALL
from pathlib import Path
from typing import Any, Dict, List

from slack_export_csv_converter.exceptions import ConverterException


class FileIO:
    """
    This is a class that absratcts away all file IO related operations
    """

    # format information consumed by csv writer
    _CSV_FORMAT = {
        "delimiter": ",",
        "quotechar": '"',
        "quoting": QUOTE_ALL,
        "escapechar": "\\",
        "doublequote": False,
        "lineterminator": "\n",
    }

    def read_json(self, file_path: Path) -> Dict[str, Any]:
        """Reads content of json file and returns a dictionary

        Args:
            file_path: path to the file to read

        Returns:
            A dictionary representation of the json file content
        """
        try:
            with file_path.open("r", encoding="utf-8") as fp:
                return json.load(fp)
        except json.JSONDecodeError as e:
            raise ConverterException(str(e))

    def csv_write(
        self,
        file_path: Path,
        fields: List[str],
        data: List[Dict[str, Any]],
        append: bool = False,
    ) -> None:
        """Writes data to a file in csv format.

        Args:
            file_path: file path of the file to be written to
            fields: column names the csv file should have, placed on the first row
            data: data to write, each row dict must have keys defined in 'fields'
            append: a flag to tell whether the 'file_path' should be appended or created
                newly

        Returns:
            None
        """
        write_mode = "w" if append is False else "a"
        try:
            with file_path.open(write_mode, encoding="utf-8", newline="") as fp:
                writer = DictWriter(fp, fields, **self._CSV_FORMAT)

                if append is False:
                    writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise ConverterException(str(e))
