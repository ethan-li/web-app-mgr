import base64
from io import BytesIO

import pytest
from PIL import Image
import numpy as np

from app.core.flask_service import FlaskWebService
from app.core.fastapi_service import FastAPIWebService
from app.apps.image_processor import ImageProcessor
from app.apps.data_analyzer import DataAnalyzer

@pytest.fixture
def flask_service():
    service = FlaskWebService()
    service.app_manager.register_app_type("image_processor", ImageProcessor)
    service.app_manager.register_app_type("data_analyzer", DataAnalyzer)
    return service
    
@pytest.fixture
def fastapi_service():
    service = FastAPIWebService()
    service.app_manager.register_app_type("image_processor", ImageProcessor)
    service.app_manager.register_app_type("data_analyzer", DataAnalyzer)
    return service
    
def create_test_image():
    """Create a test image"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode()
    
def test_image_processor(flask_service):
    """test image processor"""
    # create app instance
    app_id = flask_service.app_manager.create_app_instance("image_processor")
    app = flask_service.app_manager.get_app(app_id)
    assert app is not None
    
    # upload config
    test_image = create_test_image()
    app.upload_config("input", {"image_base64": test_image})
    app.upload_config("enhancement", {
        "brightness": 1.2,
        "contrast": 1.1,
        "sharpness": 1.3
    })
    
    # validate configs
    assert app.validate_configs() is True
    
    # start app
    app.start()
    assert app.is_running is True
    
    # wait for processing to complete
    import time
    max_wait = 10
    while app.get_status()["progress"] < 100 and max_wait > 0:
        time.sleep(1)
        max_wait -= 1
        
    # check results
    status = app.get_status()
    assert status["progress"] == 100
    assert "preview" in status
    
    report = app.get_report()
    assert "processed_image" in report
    assert "enhancement_params" in report
    
    # stop app
    app.stop()
    assert app.is_running is False
    
def test_data_analyzer(flask_service):
    """test data analyzer"""
    # create app instance
    app_id = flask_service.app_manager.create_app_instance("data_analyzer")
    app = flask_service.app_manager.get_app(app_id)
    assert app is not None
    
    # generate test data
    test_data = np.random.normal(0, 1, 1000).tolist()
    
    # upload config
    app.upload_config("data", {"values": test_data})
    app.upload_config("analysis", {"metrics": ["mean", "median", "std", "histogram"]})
    
    # validate configs
    assert app.validate_configs() is True
    
    # start app
    app.start()
    assert app.is_running is True
    
    # wait for analysis to complete
    import time
    max_wait = 10
    while app.get_status()["progress"] < 100 and max_wait > 0:
        time.sleep(1)
        max_wait -= 1
        
    # check results
    status = app.get_status()
    assert status["progress"] == 100
    assert "partial_results" in status
    assert "plot" in status
    
    report = app.get_report()
    assert "data_info" in report
    assert "analysis_results" in report
    assert "plot" in report
    
    # validate analysis results
    results = report["analysis_results"]
    assert abs(results["mean"]) < 0.1  # expect close to 0
    assert abs(results["std"] - 1.0) < 0.1  # expect close to 1
    
    # stop app
    app.stop()
    assert app.is_running is False
    
def test_invalid_configs():
    """test invalid configs"""
    # create image processor app
    app = ImageProcessor("test")
    
    # test missing required configs
    assert app.validate_configs() is False
    
    # test invalid image processor configs
    app.upload_config("input", {"wrong_key": "data"})
    app.upload_config("enhancement", {"brightness": 1.0})
    assert app.validate_configs() is False
    
    # create data analyzer app
    app = DataAnalyzer("test")
    
    # test missing required configs
    assert app.validate_configs() is False
    
    # test invalid data analyzer configs
    app.upload_config("data", {"wrong_key": []})
    app.upload_config("analysis", {"metrics": ["invalid_metric"]})
    assert app.validate_configs() is False 