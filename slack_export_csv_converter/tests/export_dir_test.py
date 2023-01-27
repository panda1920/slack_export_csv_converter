from pathlib import Path

import pytest

from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.exceptions import ConverterException

@pytest.fixture(scope="function")
def export_dir(tmp_path) -> ExportDir:
  return ExportDir(tmp_path)

class TestExportDir:
  TEST_CHANNELS = [
    'channel1',
    'チャンネル2',
    'channel 三'
  ]

  def should_accept_path_ctor(self, tmp_path):
    ExportDir(tmp_path)

  def should_throw_when_nonexistant_path(self):
    nonexisting = Path('/some/random/path/not/exist/123123123/')

    with pytest.raises(ConverterException):
      ExportDir(nonexisting)

  def should_return_users_file_path(self, export_dir: ExportDir, tmp_path: Path):
      expected_users_file = tmp_path / ExportDir.USERS_FILE_NAME
      expected_users_file.touch()

      users_file = export_dir.get_users_file()

      assert expected_users_file == users_file

  def should_throw_when_users_file_not_exist(self, export_dir: ExportDir):
    with pytest.raises(ConverterException):
      export_dir.get_users_file()

  def should_return_channel_dirs(self, export_dir: ExportDir, tmp_path: Path):
      expected_channel_dirs = [
        tmp_path / channel for channel in self.TEST_CHANNELS
      ]
      for dir in expected_channel_dirs:
        dir.mkdir()

      channel_dirs = export_dir.get_channel_dirs()
      assert len(expected_channel_dirs) == len(channel_dirs)
      for dir in channel_dirs:
        assert dir in expected_channel_dirs

  def should_return_empty_list_when_no_channel(self, export_dir: ExportDir):
      expected_channel_dirs = []

      channel_dirs = export_dir.get_channel_dirs()
      assert len(expected_channel_dirs) == len(channel_dirs)
      assert expected_channel_dirs == channel_dirs
  
  # should return multiple files for messages
  # should return 0 file when channel empty
  # should return only json files
  # should throw when not exist
  # should throw when channel not exist
