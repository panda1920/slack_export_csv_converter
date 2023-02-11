import pytest
from typing import Dict, Any

from slack_export_csv_converter.csv_data_generator import CSVDataGenerator

# Research on how to mock classes
# Do all classes need abc?


@pytest.fixture(scope="function")
def csv_data_generator() -> CSVDataGenerator:
    return CSVDataGenerator()


@pytest.mark.skip()
def shouldReadUserFileOnInstantiation(csv_data_generator: CSVDataGenerator):
    ...


class TestGenerateMessages:
    @pytest.mark.skip()
    def shouldReturnFieldNames(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateListOfData(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateDataWithRequiredFields(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldConvertTimestampToDatetimeString(
        self, csv_data_generator: CSVDataGenerator
    ):
        ...

    @pytest.mark.skip()
    def shouldGenerateUsernameBasedOnUserData(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateUnknownUsernameWhenUserIdIsNotFound(
        self, csv_data_generator: CSVDataGenerator
    ):
        ...

    @pytest.mark.skip()
    def shouldGenerateText(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateThreadFieldWhenMessageIsThreaded(
        self, csv_data_generator: CSVDataGenerator
    ):
        ...

    @pytest.mark.skip()
    def shouldIgnoreNonMessages(self, csv_data_generator: CSVDataGenerator):
        ...


class TestGenerateAttachedFiles:
    @pytest.mark.skip()
    def shouldReturnFieldNames(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateListOfData(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateDataWithRequiredFields(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldNotGenerateDataWhenFilesNotAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        ...

    @pytest.mark.skip()
    def shouldNotGenerateDataWhenDownloadNotAvailable(
        self, csv_data_generator: CSVDataGenerator
    ):
        ...

    @pytest.mark.skip()
    def shouldConvertTimestampToJapanTime(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldHaveTimestampOfEmbeddingMessage(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateUrlWithoutBackslash(self, csv_data_generator: CSVDataGenerator):
        ...

    @pytest.mark.skip()
    def shouldGenerateFilename(self, csv_data_generator: CSVDataGenerator):
        ...


def create_test_message_data(**kwargs) -> Dict[str, Any]:
    """Creates a dict that simulates exported slack message datastructure.

    Args:
        Keyword arguments that adds to/replaces default data.

    Returns:
        A dict of slack message data.
    """
    return {**DEFAULT_MESSAGE_DATA, **kwargs}


# default data used by create_test_message_data()
DEFAULT_MESSAGE_DATA = {
    "client_msg_id": "some_id",
    "type": "message",
    "text": "default text",
    "user": "XXXXXXXXXXX",
    "ts": "1672531200.000000",  # 2023-01-01 00:00:00
    "blocks": [
        {
            "type": "rich_text",
            "block_id": "XXXX",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [{"type": "text", "text": "default text"}],
                }
            ],
        }
    ],
    "team": "YYYYYYYYYYY",
    "user_team": "YYYYYYYYYYY",
    "source_team": "YYYYYYYYYYY",
    "user_profile": {
        "avatar_hash": "93c16a2e6552",
        "image_72": "https:\/\/example.com\/2023-01-01\/99999999999.png",
        "first_name": "Name",
        "real_name": "Default Name",
        "display_name": "Default Name",
        "team": "YYYYYYYYYYY",
        "name": "Default Name",
        "is_restricted": False,
        "is_ultra_restricted": False,
    },
}
