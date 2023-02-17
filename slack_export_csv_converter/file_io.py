# -*- coding: utf-8 -*-
import json
import logging
from csv import DictWriter, QUOTE_ALL
from pathlib import Path
from typing import Any, Dict, Union

from .exceptions import ConverterException
from .types import CSVData, CSVFields, ExportFileContent


class FileIO:
    """
    This is a class that absratcts away all file IO related operations.
    Makes consumers of this class more testable by isolating the file related
    responsibilities here.
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

    def __init__(self, csv_encoding="utf-8") -> None:
        self._csv_encoding = csv_encoding

    def read_json(self, file_path: Path) -> Union[Dict[str, Any], ExportFileContent]:
        """Reads content of json file and returns its content

        Args:
            file_path: path to the file to read

        Returns:
            An object representation of json file
        """
        logging.debug(f"Reading file {str(file_path)}")

        try:
            with file_path.open("r", encoding="utf-8") as fp:
                return json.load(fp)
        except json.JSONDecodeError as e:
            raise ConverterException(str(e))

    def csv_write(
        self,
        file_path: Path,
        fields: CSVFields,
        data: CSVData,
        append: bool = False,
    ) -> None:
        """Writes data to a file in csv format.

        Args:
            file_path: path of the file to be written to
            fields: column names the csv file should have, placed on the first row
            data: data to write, each row dict must have keys defined in 'fields'
            append: a flag to tell whether the 'file_path' should be appended or created
                newly during write

        Returns:
            None
        """
        logging.debug(f"Writing to file {str(file_path)}")

        write_mode = "w" if append is False else "a"
        try:
            with file_path.open(
                write_mode, encoding=self._csv_encoding, newline=""
            ) as fp:
                writer = DictWriter(fp, fields, **self._CSV_FORMAT)

                if append is False:
                    writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise ConverterException(str(e))
