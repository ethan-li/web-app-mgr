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
    """创建测试图像"""
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode()
    
def test_image_processor(flask_service):
    """测试图像处理应用"""
    # 创建应用实例
    app_id = flask_service.app_manager.create_app_instance("image_processor")
    app = flask_service.app_manager.get_app(app_id)
    assert app is not None
    
    # 上传配置
    test_image = create_test_image()
    app.upload_config("input", {"image_base64": test_image})
    app.upload_config("enhancement", {
        "brightness": 1.2,
        "contrast": 1.1,
        "sharpness": 1.3
    })
    
    # 验证配置
    assert app.validate_configs() is True
    
    # 启动应用
    app.start()
    assert app.is_running is True
    
    # 等待处理完成
    import time
    max_wait = 10
    while app.get_status()["progress"] < 100 and max_wait > 0:
        time.sleep(1)
        max_wait -= 1
        
    # 检查结果
    status = app.get_status()
    assert status["progress"] == 100
    assert "preview" in status
    
    report = app.get_report()
    assert "processed_image" in report
    assert "enhancement_params" in report
    
    # 停止应用
    app.stop()
    assert app.is_running is False
    
def test_data_analyzer(flask_service):
    """测试数据分析应用"""
    # 创建应用实例
    app_id = flask_service.app_manager.create_app_instance("data_analyzer")
    app = flask_service.app_manager.get_app(app_id)
    assert app is not None
    
    # 生成测试数据
    test_data = np.random.normal(0, 1, 1000).tolist()
    
    # 上传配置
    app.upload_config("data", {"values": test_data})
    app.upload_config("analysis", {"metrics": ["mean", "median", "std", "histogram"]})
    
    # 验证配置
    assert app.validate_configs() is True
    
    # 启动应用
    app.start()
    assert app.is_running is True
    
    # 等待分析完成
    import time
    max_wait = 10
    while app.get_status()["progress"] < 100 and max_wait > 0:
        time.sleep(1)
        max_wait -= 1
        
    # 检查结果
    status = app.get_status()
    assert status["progress"] == 100
    assert "partial_results" in status
    assert "plot" in status
    
    report = app.get_report()
    assert "data_info" in report
    assert "analysis_results" in report
    assert "plot" in report
    
    # 验证分析结果
    results = report["analysis_results"]
    assert abs(results["mean"]) < 0.1  # 期望接近0
    assert abs(results["std"] - 1.0) < 0.1  # 期望接近1
    
    # 停止应用
    app.stop()
    assert app.is_running is False
    
def test_invalid_configs():
    """测试无效配置"""
    # 创建图像处理应用
    app = ImageProcessor("test")
    
    # 测试缺少必要配置
    assert app.validate_configs() is False
    
    # 测试无效的图像处理配置
    app.upload_config("input", {"wrong_key": "data"})
    app.upload_config("enhancement", {"brightness": 1.0})
    assert app.validate_configs() is False
    
    # 创建数据分析应用
    app = DataAnalyzer("test")
    
    # 测试缺少必要配置
    assert app.validate_configs() is False
    
    # 测试无效的数据分析配置
    app.upload_config("data", {"wrong_key": []})
    app.upload_config("analysis", {"metrics": ["invalid_metric"]})
    assert app.validate_configs() is False 