from slack_export_csv_converter.convert import return_hello


def test_hello():
    assert return_hello() == "hello"
