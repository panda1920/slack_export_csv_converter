# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import List, cast
import logging
import os

from slack_export_csv_converter.logger import setup_logger
from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.file_io import FileIO
from slack_export_csv_converter.csv_data_generator import CSVDataGenerator
from slack_export_csv_converter.converter import Converter
from slack_export_csv_converter.types import ExportFileContent
from slack_export_csv_converter.exceptions import ConverterException


def main(args):
    try:
        setup_logger()
        path_args = convert_args_to_path(validate_args(sanitize_args(args)))
        converter = setup_converter(path_args)
        converter.run()
    except Exception as e:
        logging.critical(str(e))
        exit(1)


def sanitize_args(args: List[str]) -> List[str]:
    sanitized_args = []
    for arg in args:
        sanitized_arg = arg.strip()
        if sanitized_arg:
            sanitized_args.append(sanitized_arg)

    return sanitized_args


def validate_args(args: List[str]) -> List[str]:
    if len(args) < 1:
        raise ConverterException("有効なパスを1つまたは2つ指定してください。")
    if len(args) > 2:
        raise ConverterException("引数が多すぎます。有効なパスを1つまたは2つ指定してください。")
    if len(args) == 1:
        args.append(os.getcwd())

    return args


def convert_args_to_path(args: List[str]) -> List[Path]:
    return [Path(arg) for arg in args]


def setup_converter(paths: List[Path]) -> Converter:
    export_dir = ExportDir(*paths)
    file_io = FileIO()
    users_file_content = cast(
        ExportFileContent, file_io.read_json(export_dir.get_users_file())
    )
    csv_data_generator = CSVDataGenerator(users_file_content)

    return Converter(export_dir, file_io, csv_data_generator)


if __name__ == "__main__":
    main(sys.argv[1:])
