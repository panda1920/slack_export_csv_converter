import pytest
from typing import Dict, Any, List
from pathlib import Path
import json

# import logging

from slack_export_csv_converter.csv_data_generator import CSVDataGenerator


# mocks
@pytest.fixture(scope="function")
def csv_data_generator() -> CSVDataGenerator:
    return CSVDataGenerator(TEST_USERS_DATA)


class TestGetMessageFields:
    def shouldReturnFieldNames(self, csv_data_generator: CSVDataGenerator):
        fields = csv_data_generator.get_message_fields()

        assert "ts" in fields
        assert "投稿日時" in fields
        assert "ユーザー" in fields
        assert "テキスト" in fields
        assert "thread_ts" in fields


class TestGenerateMessages:
    def shouldGenerateListOfData(self, csv_data_generator: CSVDataGenerator):
        test_messages_data = [
            create_test_message_data(),
            create_test_message_data(),
            create_test_message_data(),
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        assert len(data) == len(test_messages_data)
        for message in data:
            assert "ts" in message
            assert "投稿日時" in message
            assert "ユーザー" in message
            assert "テキスト" in message
            assert "thread_ts" in message

    def shouldGenerateTsAsString(self, csv_data_generator: CSVDataGenerator):
        test_messages_data = [
            create_test_message_data(text="Some text 1", ts="1672531200.000000"),
            create_test_message_data(text="Some text 2", ts="1672531201.000000"),
            create_test_message_data(text="Some text 3", ts="1672531202.000000"),
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message, expected_message in zip(data, test_messages_data):
            assert message["ts"] == str(expected_message["ts"])

    def shouldConvertTimestampToLocalDatetimeString(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_messages_data = [
            create_test_message_data(ts="1672531200.000000"),
            create_test_message_data(ts="1672531201.000000"),
            create_test_message_data(ts="1672531202.000000"),
        ]
        # the local time for me is jst, utc + 9hrs
        expected_dates = [
            "2023-01-01 09:00:00",
            "2023-01-01 09:00:01",
            "2023-01-01 09:00:02",
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message, expected_date in zip(data, expected_dates):
            assert message["投稿日時"] == expected_date

    def shouldGenerateUsernameBasedOnUserData(self):
        for user in TEST_USERS_DATA:
            csv_data_generator = CSVDataGenerator(TEST_USERS_DATA)
            test_messages_data = [
                create_test_message_data(user=user["id"], text="some text 1"),
                create_test_message_data(user=user["id"], text="some text 2"),
                create_test_message_data(user=user["id"], text="some text 3"),
            ]

            data = csv_data_generator.generate_messages(test_messages_data)

            for message in data:
                assert message["ユーザー"] == user["name"]

    def shouldGenerateUnknownUsernameWhenUserIdIsNotFound(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_messages_data = [
            create_test_message_data(user="132719283789123", text="some text 1"),
            create_test_message_data(user="Unknown", text="some text 2"),
            create_test_message_data(user="Deleted user", text="some text 3"),
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message in data:
            assert message["ユーザー"] == "Not available"

    def shouldGenerateTextAsIs(self, csv_data_generator: CSVDataGenerator):
        test_messages_data = [
            create_test_message_data(text="Some text 1"),
            create_test_message_data(text="Some text 2"),
            create_test_message_data(text="Some text 3"),
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message, expected_message in zip(data, test_messages_data):
            assert message["テキスト"] == expected_message["text"]

    def shouldPopoulateThreadFieldWhenMessageIsThreaded(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_messages_data = [
            create_test_message_data(
                ts="1672531200.000000", text="Some text 1", thread_ts="1672531200.000000"
            ),
            create_test_message_data(
                ts="1672531210.000000", text="Some text 2", thread_ts="1672531200.000000"
            ),
            create_test_message_data(
                ts="1672531220.000000", text="Some text 3", thread_ts="1672531200.000000"
            ),
        ]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message, expected_message in zip(data, test_messages_data):
            assert message["thread_ts"] == str(expected_message["thread_ts"])

    def shouldNotPopoulateThreadFieldWhenMessageIsNotThreaded(
        self, csv_data_generator: CSVDataGenerator
    ):
        threaded_data = [
            create_test_message_data(
                ts="1672531200.000000", text="Some text 1", thread_ts="1672531200.000000"
            ),
            create_test_message_data(
                ts="1672531210.000000", text="Some text 2", thread_ts="1672531200.000000"
            ),
            create_test_message_data(
                ts="1672531220.000000", text="Some text 3", thread_ts="1672531200.000000"
            ),
        ]
        non_threaded_data = [
            create_test_message_data(ts="1672531230.000000", text="Some text 4"),
            create_test_message_data(ts="1672531240.000000", text="Some text 5"),
        ]
        test_messages_data = [*threaded_data, *non_threaded_data]

        data = csv_data_generator.generate_messages(test_messages_data)

        for message, expected_message in zip(data, test_messages_data):
            if message["テキスト"] == "Some text 4" or message["テキスト"] == "Some text 5":
                assert message["thread_ts"] == ""
            else:
                assert message["thread_ts"] == str(expected_message["thread_ts"])

    def shouldIgnoreNonMessages(self, csv_data_generator: CSVDataGenerator):
        message_data = [
            create_test_message_data(text="Some text 1", ts="1672531200.000000"),
            create_test_message_data(text="Some text 2", ts="1672531201.000000"),
            create_test_message_data(text="Some text 3", ts="1672531202.000000"),
        ]
        non_message_data = [
            create_test_message_data(
                text="Some text 2", ts="1672531204.000000", type="something"
            ),
            create_test_message_data(
                text="Some text 3", ts="1672531205.000000", type=None
            ),
        ]
        test_messages_data = [*message_data, *non_message_data]

        data = csv_data_generator.generate_messages(test_messages_data)

        assert len(data) == len(message_data)
        for message, expected_message in zip(data, message_data):
            assert message["テキスト"] == expected_message["text"]
            assert message["ts"] == str(expected_message["ts"])


class TestGetAttachmentFields:
    def shouldReturnFieldNames(self, csv_data_generator: CSVDataGenerator):
        fields = csv_data_generator.get_attachment_fields()

        assert "file_ts" in fields
        assert "アップロード日時" in fields
        assert "ユーザー" in fields
        assert "message_ts" in fields
        assert "url" in fields
        assert "ファイル名" in fields


class TestGenerateAttachedFiles:
    def shouldGenerateListOfData(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        assert len(data) == len(test_files)

    def shouldGenerateDataWithRequiredFields(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment in data:
            assert "file_ts" in attachment
            assert "アップロード日時" in attachment
            assert "ユーザー" in attachment
            assert "message_ts" in attachment
            assert "url" in attachment
            assert "ファイル名" in attachment

    def shouldGenerateTsAsStringFromCreatedField(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected in zip(data, test_files):
            assert attachment["file_ts"] == str(expected["created"])

    def shouldConvertTimestampToLocalDateTimeString(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]
        expected_file_datetimes = [
            "2023-01-01 09:00:00",
            "2023-01-01 09:00:01",
            "2023-01-01 09:00:02",
            "2023-01-01 09:00:03",
            "2023-01-01 09:00:04",
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_datetime in zip(data, expected_file_datetimes):
            assert attachment["アップロード日時"] == expected_datetime

    def shouldGenerateUsernameBasedOnUserData(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(
                text="Some text 1", files=test_files[0:2], user=TEST_USERS_DATA[0]["id"]
            ),
            create_test_message_data(
                text="Some text 2", files=test_files[2:4], user=TEST_USERS_DATA[1]["id"]
            ),
            create_test_message_data(
                text="Some text 3", files=test_files[4:], user=TEST_USERS_DATA[2]["id"]
            ),
        ]
        expected_usernames = [
            TEST_USERS_DATA[0]["name"],
            TEST_USERS_DATA[0]["name"],
            TEST_USERS_DATA[1]["name"],
            TEST_USERS_DATA[1]["name"],
            TEST_USERS_DATA[2]["name"],
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_username in zip(data, expected_usernames):
            assert attachment["ユーザー"] == expected_username

    def shouldGenerateunknownUsernameWhenNoUserDataAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(
                text="Some text 1", files=test_files[0:2], user="123123123123123"
            ),
            create_test_message_data(
                text="Some text 2", files=test_files[2:4], user="Not Exist"
            ),
            create_test_message_data(
                text="Some text 3", files=test_files[4:], user="Deleted user"
            ),
        ]
        expected_usernames = [
            "Not available",
            "Not available",
            "Not available",
            "Not available",
            "Not available",
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_username in zip(data, expected_usernames):
            assert attachment["ユーザー"] == expected_username

    def shouldHaveTsOfParentMessage(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(
                text="Some text 1", files=test_files[0:2], ts="1672531200.00000"
            ),
            create_test_message_data(
                text="Some text 2", files=test_files[2:4], ts="1672531201.00000"
            ),
            create_test_message_data(
                text="Some text 3", files=test_files[4:], ts="1672531200.00000"
            ),
        ]
        expected_ts = [
            test_message_data[0]["ts"],
            test_message_data[0]["ts"],
            test_message_data[1]["ts"],
            test_message_data[1]["ts"],
            test_message_data[2]["ts"],
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_message_ts in zip(data, expected_ts):
            assert attachment["message_ts"] == expected_message_ts

    def shouldGenerateDownloadURL(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, test_file_data in zip(data, test_files):
            assert attachment["url"] == test_file_data["url_private"]

    def shouldGenerateFilename(self, csv_data_generator: CSVDataGenerator):
        test_files = create_test_files()
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]
        expected_filenames = [
            f"{20230101090000}_{test_files[0]['name']}",
            f"{20230101090001}_{test_files[1]['name']}",
            f"{20230101090002}_{test_files[2]['name']}",
            f"{20230101090003}_{test_files[3]['name']}",
            f"{20230101090004}_{test_files[4]['name']}",
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_filename in zip(data, expected_filenames):
            assert attachment["ファイル名"] == expected_filename

    def shouldGenerateFilenameFromUrlWhenNameNotAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_files = create_test_files()
        for file in test_files[0:3]:
            file["name"] = None
        for file in test_files[3:]:
            del file["name"]
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]
        expected_filenames = [
            f"{20230101090000}_file1.png",
            f"{20230101090001}_file2.png",
            f"{20230101090002}_file3.png",
            f"{20230101090003}_file4.png",
            f"{20230101090004}_file5.png",
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        for attachment, expected_filename in zip(data, expected_filenames):
            assert attachment["ファイル名"] == expected_filename

    def shouldNotGenerateDataWhenFilesNotAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_message_data = [
            create_test_message_data(text="Some text 1", ts="1672531200.000000"),
            create_test_message_data(text="Some text 2", ts="1672531201.000000"),
            create_test_message_data(text="Some text 3", ts="1672531202.000000"),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        assert len(data) == 0

    def shouldNotGenerateDataWhenDownloadNotAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        test_files = create_test_files()
        for file in test_files[0:3]:
            file["url_private"] = None
        for file in test_files[3:]:
            del file["url_private"]
        test_message_data = [
            create_test_message_data(text="Some text 1", files=test_files[0:2]),
            create_test_message_data(text="Some text 2", files=test_files[2:4]),
            create_test_message_data(text="Some text 3", files=test_files[4:]),
        ]

        data = csv_data_generator.generate_attachments(test_message_data)

        assert len(data) == 0


# test data and creation functions
def create_test_files() -> List[Dict[str, Any]]:
    return [
        create_test_file_data(
            created=1672531200,
            url_private="https://example.com/nested/path/file1.png?hello=world#123123",
            name="file1.png",
        ),
        create_test_file_data(
            created=1672531201,
            url_private="https://example.com/nested/path/file2.png?hello=world#123123",
            name="file2.png",
        ),
        create_test_file_data(
            created=1672531202,
            url_private="https://example.com/nested/path/file3.png?hello=world#123123",
            name="file3.png",
        ),
        create_test_file_data(
            created=1672531203,
            url_private="https://example.com/nested/path/file4.png?hello=world#123123",
            name="file4.png",
        ),
        create_test_file_data(
            created=1672531204,
            url_private="https://example.com/nested/path/file5.png?hello=world#123123",
            name="file5.png",
        ),
    ]


def create_test_message_data(**kwargs) -> Dict[str, Any]:
    """Creates a dict that simulates exported slack message datastructure.

    Args:
        Keyword arguments that adds to/replaces default data.

    Returns:
        A dict of slack message data.
    """
    return {**DEFAULT_MESSAGE_DATA, **kwargs}


def create_test_file_data(**kwargs) -> Dict[str, Any]:
    """Creates a datastructure that represents files section of exported slack message.

    Args:s
        urls: downlodable url of the file uploaded to slack

    Returns:
        files datastructure in slack export
    """
    return {**DEFAULT_FILE_DATA, **kwargs}


def create_test_user_data(**kwargs) -> Dict[str, Any]:
    """Creates a user data found in slack export

    Args:
        keyword arguments that adds to/replaced user information to be created.
    Returns:
        Dict of user information
    """
    return {**DEFAULT_USER_DATA, **kwargs}


# "1672531200.000000",  # 2023-01-01 00:00:00 UCT
TEST_DATA_DIR = Path(__file__).absolute().parent / "test_data"
with (TEST_DATA_DIR / "message.json").open("r", encoding="utf-8") as f:
    # default data used by create_test_message_data()
    DEFAULT_MESSAGE_DATA = json.load(f)
with (TEST_DATA_DIR / "user.json").open("r", encoding="utf-8") as f:
    # default data used for create_user_data()
    DEFAULT_USER_DATA = json.load(f)
with (TEST_DATA_DIR / "file.json").open("r", encoding="utf-8") as f:
    # default data used for create_test_file_data()
    DEFAULT_FILE_DATA = json.load(f)
TEST_USERS_DATA = [
    create_test_user_data(id="XXXXXXXXXXX", name="Default User"),
    create_test_user_data(id="1234567890", name="John"),
    create_test_user_data(id="2345678901", name="Mary"),
    create_test_user_data(id="3456789012", name="Jane"),
]
TEST_USERS_PATH = Path("/Some/Path/To/Users.json")
TEST_MESSAGES_FILE = Path("/Some/Path/To/Channel/messages.json")
