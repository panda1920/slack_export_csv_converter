import pytest
from pathlib import Path

from slack_export_csv_converter.file_io import FileIO


TEST_JSON_DATA = """{
  "hello": "world",
  "value": 1,
  "array": [ "element one", "element two", "element 3"],
  "object": {
      "x": 123,
      "y": -19,
      "z": 188.3
  }
}"""


class TestFileIO:
    @pytest.fixture(scope="function")
    def file_io(self) -> FileIO:
        return FileIO()

    # @pytest.mark.skip()
    def shouldReadJsonFile(self, tmp_path: Path, file_io: FileIO):
        test_file = tmp_path / "test.json"
        test_file.touch()
        with test_file.open("w", encoding="utf-8") as fp:
            fp.write(TEST_JSON_DATA)

        data = file_io.read_file(test_file)

    @pytest.mark.skip()
    def shouldWriteCSVFile(self):
        ...
