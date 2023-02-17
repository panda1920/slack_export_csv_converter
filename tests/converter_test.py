import pytest
from typing import List, Dict, Any
from unittest.mock import MagicMock, create_autospec
from pathlib import Path

from slack_export_csv_converter.export_dir import ExportDir
from slack_export_csv_converter.file_io import FileIO
from slack_export_csv_converter.csv_data_generator import CSVDataGenerator
from slack_export_csv_converter.converter import Converter


# mocks
TEST_DIR_STRUCTURE = {
    "hello": [
        Path("/some/path/hello/messages1.json"),
        Path("/some/path/hello/messages2.json"),
        Path("/some/path/hello/messages3.json"),
    ],
    "world": [
        Path("/some/path/world/messages1.json"),
        Path("/some/path/world/messages2.json"),
        Path("/some/path/world/messages3.json"),
    ],
    "123": [
        Path("/some/path/123/messages1.json"),
        Path("/some/path/123/messages2.json"),
        Path("/some/path/123/messages3.json"),
    ],
    "こんにちは": [
        Path("/some/path/こんにちは/messages1.json"),
        Path("/some/path/こんにちは/messages2.json"),
        Path("/some/path/こんにちは/messages3.json"),
    ],
}
TEST_CHANNELS = list(TEST_DIR_STRUCTURE.keys())
TEST_MESSAGE_FILES = []
for channel in TEST_CHANNELS:
    TEST_MESSAGE_FILES.extend(TEST_DIR_STRUCTURE[channel])


@pytest.fixture(scope="function")
def export_dir() -> MagicMock:
    export_dir = create_autospec(ExportDir, instance=True)
    export_dir.get_channels.return_value = TEST_CHANNELS
    # get_message_files() returns list of files
    export_dir.get_message_files.side_effect = [
        files for files in TEST_DIR_STRUCTURE.values()
    ]

    return export_dir


@pytest.fixture(scope="function")
def file_io() -> MagicMock:
    file_io = create_autospec(FileIO, instance=True)
    # read_json() returns some differing data based on the argument it receives
    file_io.read_json.side_effect = create_test_json_file_content

    return file_io


def create_test_json_file_content(path: Path) -> List[Dict[str, Any]]:
    return [{"json_content": path}]


@pytest.fixture(scope="function")
def csv_data_generator() -> MagicMock:
    csv_data_generator = create_autospec(CSVDataGenerator, instance=True)

    csv_data_generator.get_message_fields.return_value = TEST_MESSAGE_FIELDS
    # generate_messages() returns tuple based on argument is receives
    csv_data_generator.generate_messages.side_effect = create_test_csv_data_messages

    csv_data_generator.get_attachment_fields.return_value = TEST_MESSAGE_FIELDS
    # generate_attachments() returns tuple based on argument is receives
    csv_data_generator.generate_attachments.side_effect = create_test_csv_data_attachments

    return csv_data_generator


TEST_MESSAGE_FIELDS = ["message_data"]
TEST_ATTACHMENT_FIELDS = ["attachment_data"]


def create_test_csv_data_messages(
    file_content: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    # refer to create_test_json_file_content() for what is in `file_content`
    return [{"message_data": file_content[0]["json_content"]}]


def create_test_csv_data_attachments(
    file_content: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    # refer to create_test_json_file_content() for what is in `file_content`
    return [{"attachment_data": file_content[0]["json_content"]}]


@pytest.fixture(scope="function")
def converter(export_dir, file_io, csv_data_generator) -> Converter:
    return Converter(export_dir, file_io, csv_data_generator)


class TestConverterRun:
    def shouldGetChannels(self, converter: Converter, export_dir: MagicMock):
        converter.run()

        export_dir.get_channels.assert_called()

    def shouldGetMessageFilesFromEachChannel(
        self, converter: Converter, export_dir: MagicMock
    ):
        export_dir.get_channels.return_value = TEST_CHANNELS

        converter.run()

        assert export_dir.get_message_files.call_count == len(TEST_CHANNELS)
        for call, expected_arg in zip(
            export_dir.get_message_files.call_args_list, TEST_CHANNELS
        ):
            (args, _) = call
            assert args[0] == expected_arg

    def shouldCallCsvChannelPathForEachChannel(
        self, converter: Converter, export_dir: MagicMock
    ):
        export_dir.get_channels.return_value = TEST_CHANNELS

        converter.run()

        assert export_dir.get_csv_channel_path.call_count == len(TEST_CHANNELS)
        for call, expected_arg in zip(
            export_dir.get_csv_channel_path.call_args_list, TEST_CHANNELS
        ):
            (args, _) = call
            assert args[0] == expected_arg

    def shouldReadJsonOfEachChannelMessageFiles(
        self, converter: Converter, export_dir: MagicMock, file_io: MagicMock
    ):
        # get_message_files() returns list of files
        export_dir.get_message_files.side_effect = [
            files for files in TEST_DIR_STRUCTURE.values()
        ]

        converter.run()

        assert file_io.read_json.call_count == len(TEST_MESSAGE_FILES)
        for call, expected_arg in zip(
            file_io.read_json.call_args_list, TEST_MESSAGE_FILES
        ):
            (args, _) = call
            assert args[0] == expected_arg

    def shouldGenerateCSVMessagesDataForEachMessageFile(
        self, converter: Converter, file_io: MagicMock, csv_data_generator: MagicMock
    ):
        # read_json() returns some differing data based on the argument it receives
        file_io.read_json.side_effect = create_test_json_file_content

        converter.run()

        assert csv_data_generator.generate_messages.call_count == len(TEST_MESSAGE_FILES)
        for message_file in TEST_MESSAGE_FILES:
            expected_file_content = create_test_json_file_content(message_file)
            csv_data_generator.generate_messages.assert_any_call(expected_file_content)

    def shouldGenerateAttachmentsDataForEachMessageFile(
        self, converter: Converter, file_io: MagicMock, csv_data_generator: MagicMock
    ):
        # read_json() returns some differing data based on the argument it receives
        file_io.read_json.side_effect = create_test_json_file_content

        converter.run()

        assert csv_data_generator.generate_attachments.call_count == len(
            TEST_MESSAGE_FILES
        )
        for message_file in TEST_MESSAGE_FILES:
            expected_file_content = create_test_json_file_content(message_file)
            csv_data_generator.generate_attachments.assert_any_call(expected_file_content)

    def shouldGatherGeneratedCSVMessagesDataOfChannelAndPassToWrite(
        self,
        converter: Converter,
        export_dir: MagicMock,
        csv_data_generator: MagicMock,
        file_io: MagicMock,
    ):
        # get_csv_channel_path() returns Path based on argument it receives
        export_dir.get_csv_channel_path.side_effect = (
            lambda channel: Path("/path/to") / channel
        )
        csv_data_generator.get_message_fields.return_value = TEST_MESSAGE_FIELDS
        # generate_messages() returns tuple based on argument is receives
        csv_data_generator.generate_messages.side_effect = create_test_csv_data_messages

        converter.run()

        for channel in TEST_CHANNELS:
            expected_file_path = Path("/path/to") / channel / "messages.csv"
            expected_fields = TEST_MESSAGE_FIELDS
            # combine data generated from files belonging to the channel
            expected_data = [
                create_test_csv_data_messages(create_test_json_file_content(file_path))[0]
                for file_path in TEST_DIR_STRUCTURE[channel]
            ]

            file_io.csv_write.assert_any_call(
                expected_file_path,
                expected_fields,
                expected_data,
            )

    def shouldGatherGeneratedCSVAttachmentsDataOfChannelAndPassToWrite(
        self,
        converter: Converter,
        export_dir: MagicMock,
        csv_data_generator: MagicMock,
        file_io: MagicMock,
    ):
        # get_csv_channel_path() returns Path based on argument it receives
        export_dir.get_csv_channel_path.side_effect = (
            lambda channel: Path("/path/to") / channel
        )
        csv_data_generator.get_attachment_fields.return_value = TEST_ATTACHMENT_FIELDS
        # generate_attachments() returns tuple based on argument is receives
        csv_data_generator.generate_attachments.side_effect = (
            create_test_csv_data_attachments
        )

        converter.run()

        for channel in TEST_CHANNELS:
            expected_file_path = Path("/path/to") / channel / "attachments.csv"
            expected_fields = TEST_ATTACHMENT_FIELDS
            # combine data generated from files belonging to the channel
            expected_data = [
                create_test_csv_data_attachments(
                    create_test_json_file_content(file_path)
                )[0]
                for file_path in TEST_DIR_STRUCTURE[channel]
            ]

            file_io.csv_write.assert_any_call(
                expected_file_path,
                expected_fields,
                expected_data,
            )
