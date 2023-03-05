import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

from slack_export_csv_converter.file_io import FileIO
from slack_export_csv_converter.exceptions import ConverterException


@pytest.fixture(scope="function")
def file_io() -> FileIO:
    return FileIO()


class TestFileIOReadJson:
    def shouldReadJsonFile(self, tmp_path: Path, file_io: FileIO):
        test_json_data_string = """{
            "hello": "world",
            "value": 1,
            "boolean": true,
            "array": [ "element one", "element two", "element 3"],
            "nested": {
                "x": 123,
                "y": -19,
                "z": 188.3
            }
        }"""
        test_json_data = json.loads(test_json_data_string)
        test_file = tmp_path / "test.json"
        test_file.touch()
        with test_file.open("w", encoding="utf-8") as fp:
            fp.write(test_json_data_string)

        data = file_io.read_json(test_file)

        assert isinstance(data, dict)

        assert data["hello"] == test_json_data["hello"]
        assert data["value"] == test_json_data["value"]
        assert data["boolean"] == test_json_data["boolean"]

        assert len(data["array"]) == len(test_json_data["array"])
        assert data["array"][0] == test_json_data["array"][0]
        assert data["array"][1] == test_json_data["array"][1]
        assert data["array"][2] == test_json_data["array"][2]

        assert data["nested"]["x"] == test_json_data["nested"]["x"]
        assert data["nested"]["y"] == test_json_data["nested"]["y"]
        assert data["nested"]["z"] == test_json_data["nested"]["z"]

    def shouldReadListJsonFile(self, tmp_path: Path, file_io: FileIO):
        test_json_data_string = """[
            1,
            2,
            3,
            4,
            "hello",
            "example.com"
        ]"""
        test_json_data = json.loads(test_json_data_string)
        test_file = tmp_path / "test.json"
        test_file.touch()
        with test_file.open("w", encoding="utf-8") as fp:
            fp.write(test_json_data_string)

        data = file_io.read_json(test_file)

        assert isinstance(data, list)

        for data, expected_data in zip(data, test_json_data):
            assert data == expected_data

    def shouldThrowWhenInvalidJsonFile(self, tmp_path: Path, file_io: FileIO):
        test_file = tmp_path / "test.json"
        test_file.touch()
        with test_file.open("w", encoding="utf-8") as fp:
            fp.write("invalid json content 123#!#(*!@#Y!@($*)")

        with pytest.raises(ConverterException):
            file_io.read_json(test_file)


class TestFileIOWriteCSV:
    def shouldWriteToCSVFile(self, tmp_path: Path, file_io: FileIO):
        test_csv_data = [
            {"column1": "hello world", "column2": 123, "column3": "2030-01-01"},
            {"column1": "foo bar baz", "column2": 999, "column3": "2030-02-01"},
            {
                "column1": 'I went to "quoted" resteraunt',
                "column2": -180,
                "column3": "2030-03-01",
            },
        ]
        test_csv_fields = [key for key in test_csv_data[0].keys()]
        test_file = tmp_path / "test.csv"
        expected_file_content = (
            '"column1","column2","column3"\n'
            '"hello world","123","2030-01-01"\n'
            '"foo bar baz","999","2030-02-01"\n'
            '"I went to \\"quoted\\" resteraunt","-180","2030-03-01"\n'
        )

        file_io.csv_write(test_file, test_csv_fields, test_csv_data)

        assert test_file.exists()
        with test_file.open("r", encoding="utf-8") as fp:
            file_content = fp.read()
            assert file_content == expected_file_content

    def shouldWriteCSVHeaderOnlyWhenNoData(self, tmp_path: Path, file_io: FileIO):
        test_csv_data = []
        test_csv_fields = ["column1", "column2", "column3"]
        test_file = tmp_path / "test.csv"
        expected_file_content = '"column1","column2","column3"\n'

        file_io.csv_write(test_file, test_csv_fields, test_csv_data)

        assert test_file.exists()
        with test_file.open("r", encoding="utf-8") as fp:
            file_content = fp.read()
            assert file_content == expected_file_content

    def shouldThrowWhenWriteCSVFails(self, tmp_path: Path, file_io: FileIO):
        bad_data = [{"wrong_field": "123"}]
        fields = ["column1", "column2", "column3"]
        test_file = tmp_path / "test.csv"

        with pytest.raises(ConverterException):
            file_io.csv_write(test_file, fields, bad_data)

    def shouldAppendToCSVFileWhenAppendIsTrue(self, tmp_path: Path, file_io: FileIO):
        test_csv_data_1 = [
            {"column1": "hello world", "column2": 123, "column3": "2030-01-01"},
        ]
        test_csv_data_2 = [
            {"column1": "foo bar baz", "column2": 999, "column3": "2030-02-01"},
            {
                "column1": 'I went to "quoted" resteraunt',
                "column2": -180,
                "column3": "2030-03-01",
            },
        ]
        test_csv_fields = [key for key in test_csv_data_1[0].keys()]
        test_file = tmp_path / "test.csv"
        expected_file_content = (
            '"column1","column2","column3"\n'
            '"hello world","123","2030-01-01"\n'
            '"foo bar baz","999","2030-02-01"\n'
            '"I went to \\"quoted\\" resteraunt","-180","2030-03-01"\n'
        )

        file_io.csv_write(test_file, test_csv_fields, test_csv_data_1)
        file_io.csv_write(test_file, test_csv_fields, test_csv_data_2, append=True)

        assert test_file.exists()
        with test_file.open("r", encoding="utf-8") as fp:
            file_content = fp.read()
            assert file_content == expected_file_content

    def shouldClearPreviousCSVFileContentWhenWriteCSVAppendIsFalse(
        self, tmp_path: Path, file_io: FileIO
    ):
        test_csv_data_1 = [
            {"column1": "hello world", "column2": 123, "column3": "2030-01-01"},
        ]
        test_csv_data_2 = [
            {"column1": "foo bar baz", "column2": 999, "column3": "2030-02-01"},
            {
                "column1": 'I went to "quoted" resteraunt',
                "column2": -180,
                "column3": "2030-03-01",
            },
        ]
        test_csv_fields = [key for key in test_csv_data_1[0].keys()]
        test_file = tmp_path / "test.csv"
        expected_file_content = (
            '"column1","column2","column3"\n'
            '"foo bar baz","999","2030-02-01"\n'
            '"I went to \\"quoted\\" resteraunt","-180","2030-03-01"\n'
        )

        file_io.csv_write(test_file, test_csv_fields, test_csv_data_1)
        file_io.csv_write(test_file, test_csv_fields, test_csv_data_2, append=False)
        # same thing when append arg is omitted because defualt is False
        # file_io.csv_write(test_file, test_csv_fields, test_csv_data_2)

        assert test_file.exists()
        with test_file.open("r", encoding="utf-8") as fp:
            file_content = fp.read()
            assert file_content == expected_file_content

    def shouldBeAbleToSpecifyEncodingOfCSVWrite(self, tmp_path: Path):
        test_csv_data = [
            {"column1": "こんにちは！", "column2": 123, "column3": "2030-01-01"},
            {"column1": "ほげふが", "column2": 999, "column3": "2030-02-01"},
            {
                "column1": 'I went to "quoted" resteraunt',
                "column2": -180,
                "column3": "2030-03-01",
            },
        ]
        test_csv_fields = [key for key in test_csv_data[0].keys()]
        test_file = tmp_path / "test.csv"
        expected_file_content = (
            '"column1","column2","column3"\n'
            '"こんにちは！","123","2030-01-01"\n'
            '"ほげふが","999","2030-02-01"\n'
            '"I went to \\"quoted\\" resteraunt","-180","2030-03-01"\n'
        )
        file_io = FileIO(csv_encoding="shift-jis")

        file_io.csv_write(test_file, test_csv_fields, test_csv_data)

        assert test_file.exists()
        with test_file.open("r", encoding="shift-jis") as fp:
            file_content = fp.read()
            assert file_content == expected_file_content


class TestFileIODownload:
    @contextmanager
    def patch_urlopen(self):
        mock = MagicMock()
        with patch(
            "slack_export_csv_converter.file_io.urlopen", new=mock
        ) as urlopen_mock:
            urlopen_mock.return_value.__enter__.return_value.read.return_value = (
                b"Some bytes"
            )
            yield urlopen_mock

    @pytest.mark.skip()
    def shouldDownloadFile(self, tmp_path: Path, file_io: FileIO):
        image_url = "https://picsum.photos/100"
        expected_file_path = tmp_path / "somge_img.jpg"

        assert not expected_file_path.exists()

        file_io.download(image_url, expected_file_path)

        assert expected_file_path.exists()

    def shouldSkipDownloadWhenFileExist(self, tmp_path: Path, file_io: FileIO):
        image_url = "https://picsum.photos/100"
        expected_file_path = tmp_path / "somge_img.jpg"
        expected_file_path.touch()

        with self.patch_urlopen() as urlopen_mock:
            file_io.download(image_url, expected_file_path)

            urlopen_mock.assert_not_called()

    def shouldRaiseConverterExceptioNWhenSomethingGoesWrong(
        self, tmp_path: Path, file_io: FileIO
    ):
        image_url = "https://picsum.photos/100"
        expected_file_path = tmp_path / "somge_img.jpg"
        error = Exception("Some error")

        with self.patch_urlopen() as urlopen_mock:
            urlopen_mock.reset_mock(side_effect=True, return_value=True)
            urlopen_mock.side_effect = error

            with pytest.raises(ConverterException):
                file_io.download(image_url, expected_file_path)

        with self.patch_urlopen() as urlopen_mock:
            urlopen_mock.return_value.__enter__.return_value.read.reset_mock(
                return_value=True
            )
            urlopen_mock.return_value.__enter__.return_value.read.side_effect = error

            with pytest.raises(ConverterException):
                file_io.download(image_url, expected_file_path)
