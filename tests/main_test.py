from main import return_hello


def test_hello():
    assert return_hello() == "hello"
