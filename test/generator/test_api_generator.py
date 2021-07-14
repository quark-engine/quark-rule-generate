
import pytest
from generator.api_generator import ApiGenerator
from model.android_sample_model import AndroidSampleModel

@pytest.fixture()
def apk_analysis(scope="function"):
    return AndroidSampleModel("test/sample/test_sample.apk")
    

class TestApiGenerator:
    
    def test_statistic(self, apk_analysis):
        apis = ApiGenerator(apk_analysis.apis)
        print(apis.statistic())