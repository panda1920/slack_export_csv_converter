import pytest
from pathlib import Path
from typing import List

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

  @pytest.fixture(scope="function")
  def create_channels(self, tmp_path: Path):
    channel_paths = []
    for channel in self.TEST_CHANNELS:
      channel_path = tmp_path / channel
      channel_path.mkdir()
      channel_paths.append(channel_path)

    return channel_paths

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

    assert users_file == expected_users_file

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

    assert len(channel_dirs) == len(expected_channel_dirs)
    for dir in channel_dirs:
      assert dir in expected_channel_dirs

  def should_return_empty_list_when_no_channel(self, export_dir: ExportDir):
    expected_channel_dirs = []

    channel_dirs = export_dir.get_channel_dirs()

    assert len(channel_dirs) == len(expected_channel_dirs)
    assert channel_dirs == expected_channel_dirs

  def should_return_messages_for_channel(self, export_dir: ExportDir, create_channels: List[Path]):
    channel_1 = create_channels[0].stem
    channel_2 = create_channels[1].stem

    # setup files for channel_1
    files_1 = [
      create_channels[0] / '1.json',
      create_channels[0] / '2.json',
      create_channels[0] / '3.json'
    ]
    # setup files for channel_2
    files_2 = [
      create_channels[1] / '11.json',
      create_channels[1] / '12.json',
      create_channels[1] / '13.json',
      create_channels[1] / '14.json',
      create_channels[1] / '15.json',
    ]
    for file in [*files_1, *files_2]:
      file.touch()
    
    messages = export_dir.get_message_files(channel_1)

    assert len(messages) == len(files_1)
    for file in messages:
      assert file in files_1

    messages = export_dir.get_message_files(channel_2)

    assert len(messages) == len(files_2)
    for file in messages:
      assert file in files_2

  def should_only_return_json_files_for_message(self, export_dir: ExportDir, create_channels: List[Path]):
    channel = create_channels[0].stem

    # setup files for channel
    json_files = [
      create_channels[0] / '1.json',
      create_channels[0] / '2.json',
      create_channels[0] / '3.json'
    ]
    non_json_files = [
      create_channels[0] / 'data.csv',
      create_channels[0] / 'some.log',
      create_channels[0] / 'notes.txt',
      create_channels[0] / 'asset.png'
    ]
    for file in [*json_files, *non_json_files]:
      file.touch()

    messages = export_dir.get_message_files(channel)

    assert len(messages) == len(json_files)
    for file in messages:
      assert file in json_files

  def should_return_no_messages_when_channel_empty(self, export_dir: ExportDir, create_channels: List[Path]):
    channel_1, channel_2, channel_3 = create_channels

    assert len(export_dir.get_message_files(channel_1)) == 0
    assert len(export_dir.get_message_files(channel_2)) == 0
    assert len(export_dir.get_message_files(channel_3)) == 0

  def should_throw_when_get_message_channel_not_exist(self, export_dir: ExportDir, create_channels: List[Path]):
    with pytest.raises(ConverterException):
      export_dir.get_message_files("NON_EXISTANT_CHANNEL")

  def should_get_channel_path_from_name(self, export_dir: ExportDir, create_channels: List[Path]):
    for expected_channel_path in create_channels:
      channel_name = expected_channel_path.stem

      channel_path = export_dir.get_channel_path(channel_name)
      
      assert channel_path == expected_channel_path

  def should_throw_when_get_channel_path_not_found(self, export_dir: ExportDir, create_channels: List[Path]):
    with pytest.raises(ConverterException):
      export_dir.get_channel_path("NON_EXISTANT_CHANNEL")
