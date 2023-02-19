import pytest
from unittest.mock import patch, sentinel
from contextlib import contextmanager
from pathlib import Path

from main import main
from slack_export_csv_converter.exceptions import ConverterException


TEST_PATH_1 = "/path/to/export"
TEST_PATH_2 = "/path/to/save/location"


class TestMain:
    @contextmanager
    def patch_dependencies(self):
        # fmt: off
        with patch("main.ExportDir") as export_dir, \
                patch("main.FileIO") as file_io, \
                patch("main.CSVDataGenerator") as csv_data_generator, \
                patch("main.Converter") as converter:
            # fmt: on
            yield (export_dir, file_io, csv_data_generator, converter)

    def shouldInitializeObjects(self):
        with self.patch_dependencies() as patches:
            (export_dir, file_io, csv_data_generator, converter) = patches

            main([TEST_PATH_1, TEST_PATH_2])

            export_dir.assert_called_once()
            file_io.assert_called_once()
            csv_data_generator.assert_called_once()
            converter.assert_called_once()

            # validate that components are built from other components
            args = converter.call_args.args
            assert args[0] is export_dir()
            assert args[1] is file_io()
            assert args[2] is csv_data_generator()

    def shouldPassArgumentToExportDir(self):
        with self.patch_dependencies() as patches:
            (export_dir, *_) = patches

            main([TEST_PATH_1, TEST_PATH_2])

            export_dir.assert_called_with(Path(TEST_PATH_1), Path(TEST_PATH_2))

    def shouldPassCwdToExportDirWhenSecondArgNotPresent(self):
        with self.patch_dependencies() as patches:
            (export_dir, *_) = patches

            main([TEST_PATH_1])

            export_dir.assert_called_with(Path(TEST_PATH_1), Path.cwd())

    def shouldSanitizeArgument(self):
        with self.patch_dependencies() as patches:
            (export_dir, *_) = patches

            main([TEST_PATH_1 + " ", TEST_PATH_2 + " "])

            export_dir.assert_called_with(Path(TEST_PATH_1), Path(TEST_PATH_2))
            export_dir.reset_mock()

            main([" " + TEST_PATH_1, " " + TEST_PATH_2])

            export_dir.assert_called_with(Path(TEST_PATH_1), Path(TEST_PATH_2))
            export_dir.reset_mock()

            main([TEST_PATH_1, " "])

            export_dir.assert_called_with(Path(TEST_PATH_1), Path.cwd())
            export_dir.reset_mock()

            main([" ", TEST_PATH_2])

            export_dir.assert_called_with(Path(TEST_PATH_2), Path.cwd())

    def shouldSpecifyCSVEncodingOfFileIO(self):
        with self.patch_dependencies() as patches:
            (_, file_io, *_) = patches

            main([TEST_PATH_1, TEST_PATH_2])

            # file_io.assert_called_With(encoding="utf-8")
            file_io.assert_called_with(csv_encoding="shift-jis")

    def shouldPassUsersFileContentToGenerator(self):
        with self.patch_dependencies() as patches:
            (export_dir, file_io, csv_data_generator, _) = patches
            export_dir().get_users_file.return_value = sentinel.users_file
            file_io().read_json.return_value = sentinel.users_file_content

            main([TEST_PATH_1])

            export_dir().get_users_file.assert_called_once()
            file_io().read_json.assert_called_once_with(sentinel.users_file)
            csv_data_generator.assert_called_once_with(sentinel.users_file_content)

    def shouldRunConverter(self):
        with self.patch_dependencies() as patches:
            (_, _, _, converter) = patches

            main([TEST_PATH_1])

            converter().run.assert_called_once()

    def shouldExitAndNotRunConverterWhenNoArguments(self):
        with self.patch_dependencies() as patches:
            (_, _, _, converter) = patches

            with pytest.raises(SystemExit):
                main([])

            converter().run.assert_not_called()

    def shouldExitAndNotRunConverterWhenTooMuchArguments(self):
        with self.patch_dependencies() as patches:
            (_, _, _, converter) = patches

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2, "123"])
                main([TEST_PATH_1, TEST_PATH_2, "123", "hello", "world"])

            converter().run.assert_not_called()

    def shouldExitWhenException(self):
        with self.patch_dependencies() as patches:
            (export_dir, file_io, csv_data_generator, converter) = patches

            export_dir.side_effect = ConverterException("Something")

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2])

            export_dir.reset_mock(side_effect=True)
            file_io.side_effect = ConverterException("Something")

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2])

            file_io.reset_mock(side_effect=True)
            csv_data_generator.side_effect = ConverterException("Something")

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2])

            csv_data_generator.reset_mock(side_effect=True)
            converter.side_effect = ConverterException("Something")

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2])

            converter.reset_mock(side_effect=True)
            converter().run.side_effect = ConverterException("Something")

            with pytest.raises(SystemExit):
                main([TEST_PATH_1, TEST_PATH_2])
