import pytest
from pprint import pprint
from model.android_sample_model import AndroidSampleModel

@pytest.fixture(scope="function")
def invalid_file(tmp_path):
    invalid_file = tmp_path / "invalid_file.txt"
    invalid_file.write_text("Not apk file")

    yield invalid_file

@pytest.fixture(scope="function")
def valid_file():
    return "test/sample/test_sample.apk"

class TestAndroidSampleModel:
    
    def test_apis(self, valid_file):
        pass
