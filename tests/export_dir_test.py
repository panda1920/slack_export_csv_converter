import pytest
from pathlib import Path
from typing import List

from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.exceptions import ConverterException


class TestExportDir:
    TEST_CHANNELS = ["channel1", "チャンネル2", "channel 三"]

    @pytest.fixture(scope="function")
    def export_path(self, tmp_path) -> Path:
        path = tmp_path / "export"
        path.mkdir()
        return path

    @pytest.fixture(scope="function")
    def csv_path(self, tmp_path) -> Path:
        return tmp_path / "csv"

    @pytest.fixture(scope="function")
    def export_dir(self, export_path, csv_path) -> ExportDir:
        return ExportDir(export_path, csv_path)

    @pytest.fixture(scope="function")
    def create_channels(self, export_path: Path) -> List[Path]:
        channel_paths = []
        for channel in self.TEST_CHANNELS:
            channel_path = export_path / channel
            channel_path.mkdir()
            channel_paths.append(channel_path)

        return channel_paths

    def shouldAcceptPathForCtor(self, export_path, csv_path):
        ExportDir(export_path, csv_path)

    def shouldThrowWhenNonexistantCtorPath(self, csv_path):
        nonexisting = Path("/some/random/path/not/exist/123123123/")

        with pytest.raises(ConverterException):
            ExportDir(nonexisting, csv_path)

    def shouldReturnUsersFilePath(self, export_dir: ExportDir, export_path: Path):
        expected_users_file = export_path / ExportDir._USERS_FILE_NAME
        expected_users_file.touch()

        users_file = export_dir.get_users_file()

        assert users_file == expected_users_file

    def shouldThrowWhenUsersFileNotExist(self, export_dir: ExportDir):
        with pytest.raises(ConverterException):
            export_dir.get_users_file()

    def shouldReturnChannelNames(self, export_path: Path, csv_path: Path):
        channel_path = [export_path / channel for channel in self.TEST_CHANNELS]
        for dir in channel_path:
            dir.mkdir()
        export_dir = ExportDir(export_path, csv_path)

        channel_dirs = export_dir.get_channels()

        assert len(channel_dirs) == len(self.TEST_CHANNELS)
        for dir in channel_dirs:
            assert dir in self.TEST_CHANNELS

    def shouldReturnEmptyListWhenNoChannel(self, export_dir: ExportDir):
        expected_channel_names = []

        channel_dirs = export_dir.get_channels()

        assert len(channel_dirs) == len(expected_channel_names)
        assert channel_dirs == expected_channel_names

    def shouldReturnMessagesForChannel(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
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
        self, create_channels: List[Path], export_dir: ExportDir
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
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[0])) == 0
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[1])) == 0
        assert len(export_dir.get_message_files(self.TEST_CHANNELS[2])) == 0

    def shouldThrowWhenChannelNotExistForGetMessage(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        with pytest.raises(ConverterException):
            export_dir.get_message_files("NON_EXISTANT_CHANNEL")

    def shouldGetCSVChannelPathFromName(
        self,
        tmp_path: Path,
        export_path: Path,
        create_channels: List[Path],
    ):
        expected_csv_path = tmp_path / "some" / "path"
        export_dir = ExportDir(export_path, expected_csv_path)

        for channel in self.TEST_CHANNELS:
            expected_path = expected_csv_path / channel

            csv_channel_path = export_dir.get_csv_channel_path(channel)

            assert csv_channel_path == expected_path

    def shouldCreateCSVChannelPathFromName(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        for channel in self.TEST_CHANNELS:
            csv_channel_path = export_dir.get_csv_channel_path(channel)

            assert csv_channel_path.exists()

    def shouldThrowWhenGetCSVChannelPathNotExist(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        with pytest.raises(ConverterException):
            export_dir.get_csv_channel_path("NON_EXISTANT_CHANNEL")

    def shouldGetAttachmentsPathFromChannelName(
        self, csv_path: Path, create_channels: List[Path], export_dir: ExportDir
    ):
        for channel in self.TEST_CHANNELS:
            expected_path = csv_path / channel / "attachments"

            attachments_path = export_dir.get_attachments_path(channel)

            assert attachments_path == expected_path

    def shouldCreateAttachmentsPathFromChannelName(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        for channel in self.TEST_CHANNELS:
            attachments_path = export_dir.get_attachments_path(channel)

            assert attachments_path.exists()

    def shouldThrowWhenChannelForAttachmentPathNotExist(
        self, create_channels: List[Path], export_dir: ExportDir
    ):
        with pytest.raises(ConverterException):
            export_dir.get_attachments_path("NON_EXISTANT_CHANNEL")
