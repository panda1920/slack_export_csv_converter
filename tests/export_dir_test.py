import pytest
from pathlib import Path
from typing import List

from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.exceptions import ConverterException


class TestExportDir:
    TEST_CHANNELS = ["channel1", "チャンネル2", "channel 三"]

    @pytest.fixture(scope="function")
    def export_dir(self, tmp_path) -> ExportDir:
        return ExportDir(tmp_path)

    @pytest.fixture(scope="function")
    def create_channels(self, tmp_path: Path) -> List[Path]:
        channel_paths = []
        for channel in self.TEST_CHANNELS:
            channel_path = tmp_path / channel
            channel_path.mkdir()
            channel_paths.append(channel_path)

        return channel_paths

    def shouldAcceptPathForCtor(self, tmp_path):
        ExportDir(tmp_path)

    def shouldThrowWhenNonexistantCtorPath(self):
        nonexisting = Path("/some/random/path/not/exist/123123123/")

        with pytest.raises(ConverterException):
            ExportDir(nonexisting)

    def shouldReturnUsersFilePath(self, export_dir: ExportDir, tmp_path: Path):
        expected_users_file = tmp_path / ExportDir.USERS_FILE_NAME
        expected_users_file.touch()

        users_file = export_dir.get_users_file()

        assert users_file == expected_users_file

    def shouldThrowWhenUsersFileNotExist(self, export_dir: ExportDir):
        with pytest.raises(ConverterException):
            export_dir.get_users_file()

    def shouldReturnChannelDirs(self, export_dir: ExportDir, tmp_path: Path):
        expected_channel_dirs = [tmp_path / channel for channel in self.TEST_CHANNELS]
        for dir in expected_channel_dirs:
            dir.mkdir()

        channel_dirs = export_dir.get_channel_dirs()

        assert len(channel_dirs) == len(expected_channel_dirs)
        for dir in channel_dirs:
            assert dir in expected_channel_dirs

    def shouldReturnEmptyListWhenNoChannel(self, export_dir: ExportDir):
        expected_channel_dirs = []

        channel_dirs = export_dir.get_channel_dirs()

        assert len(channel_dirs) == len(expected_channel_dirs)
        assert channel_dirs == expected_channel_dirs

    def shouldReturnMessagesForChannel(self, export_dir: ExportDir, create_channels: List[Path]):
        channel_1 = create_channels[0].stem
        channel_2 = create_channels[1].stem

        # setup files for channel_1
        files_1 = [
            create_channels[0] / "1.json",
            create_channels[0] / "2.json",
            create_channels[0] / "3.json",
        ]
        # setup files for channel_2
        files_2 = [
            create_channels[1] / "11.json",
            create_channels[1] / "12.json",
            create_channels[1] / "13.json",
            create_channels[1] / "14.json",
            create_channels[1] / "15.json",
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

    def shouldOnlyReturnJsonFilesForMessage(
        self, export_dir: ExportDir, create_channels: List[Path]
    ):
        channel = create_channels[0].stem

        # setup files for channel
        json_files = [
            create_channels[0] / "1.json",
            create_channels[0] / "2.json",
            create_channels[0] / "3.json",
        ]
        non_json_files = [
            create_channels[0] / "data.csv",
            create_channels[0] / "some.log",
            create_channels[0] / "notes.txt",
            create_channels[0] / "asset.png",
        ]
        for file in [*json_files, *non_json_files]:
            file.touch()

        messages = export_dir.get_message_files(channel)

        assert len(messages) == len(json_files)
        for file in messages:
            assert file in json_files

    def shouldReturnNoMessagesWhenChannelEmpty(
        self, export_dir: ExportDir, create_channels: List[Path]
    ):
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[0])) == 0
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[1])) == 0
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[2])) == 0

    def shouldThrowWhenChannelNotExistForGetMessage(
        self, export_dir: ExportDir, create_channels: List[Path]
    ):
        with pytest.raises(ConverterException):
            export_dir.get_message_files("NON_EXISTANT_CHANNEL")

    def shouldGetChannelPathFromName(self, export_dir: ExportDir, create_channels: List[Path]):
        for expected_channel_path in create_channels:
            channel_name = expected_channel_path.stem

            channel_path = export_dir.get_channel_path(channel_name)

            assert channel_path == expected_channel_path

    def shouldThrowWhenGetChannelPathNotExist(
        self, export_dir: ExportDir, create_channels: List[Path]
    ):
        with pytest.raises(ConverterException):
            export_dir.get_channel_path("NON_EXISTANT_CHANNEL")
