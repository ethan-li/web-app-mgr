import time
import threading
from typing import Dict, Any
import base64
from io import BytesIO

from PIL import Image, ImageEnhance

from app.core.base_app import BaseApp

class ImageProcessor(BaseApp):
    def __init__(self, app_id: str):
        super().__init__(app_id)
        self.required_configs = ["input", "enhancement"]
        self.processing_thread = None
        self.current_image = None
        self.enhanced_image = None
        self.progress = 0
        
    def validate_configs(self) -> bool:
        """Validate configuration files"""
        if not all(config in self.configs for config in self.required_configs):
            return False
            
        # Validate input configuration
        input_config = self.configs["input"]
        if "image_base64" not in input_config:
            return False
            
        # Validate enhancement configuration
        enhancement_config = self.configs["enhancement"]
        if not all(key in enhancement_config for key in ["brightness", "contrast", "sharpness"]):
            return False
            
        return True
        
    def _process_image(self):
        """Process image in background thread"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(self.configs["input"]["image_base64"])
            self.current_image = Image.open(BytesIO(image_data))
            self.progress = 20
            
            # Apply enhancements
            enhancement = self.configs["enhancement"]
            self.enhanced_image = self.current_image
            
            # Adjust brightness
            enhancer = ImageEnhance.Brightness(self.enhanced_image)
            self.enhanced_image = enhancer.enhance(enhancement["brightness"])
            self.progress = 40
            
            # Adjust contrast
            enhancer = ImageEnhance.Contrast(self.enhanced_image)
            self.enhanced_image = enhancer.enhance(enhancement["contrast"])
            self.progress = 60
            
            # Adjust sharpness
            enhancer = ImageEnhance.Sharpness(self.enhanced_image)
            self.enhanced_image = enhancer.enhance(enhancement["sharpness"])
            self.progress = 80
            
            # Simulate processing time
            time.sleep(2)
            self.progress = 100
            
        except Exception as e:
            self.progress = -1
            raise e
            
    def start(self) -> None:
        """Start image processing"""
        if self.is_running:
            raise RuntimeError("Application is already running")
            
        self.progress = 0
        self.processing_thread = threading.Thread(target=self._process_image)
        self.processing_thread.start()
        self.is_running = True
        
    def stop(self) -> None:
        """Stop image processing"""
        if not self.is_running:
            raise RuntimeError("Application is not running")
            
        if self.processing_thread and self.processing_thread.is_alive():
            # In a real application, there should be a more graceful way to stop
            self.processing_thread.join(timeout=1)
            
        self.is_running = False
        self.progress = 0
        
    def get_status(self) -> Dict[str, Any]:
        """Get processing status"""
        status = {
            "progress": self.progress,
            "is_running": self.is_running,
            "app_type": "image_processor"
        }
        
        # If there's a current image, add preview
        if self.enhanced_image and self.progress > 0:
            preview = BytesIO()
            preview_size = (200, 200)  # Reduce preview image size
            preview_image = self.enhanced_image.copy()
            preview_image.thumbnail(preview_size)
            preview_image.save(preview, format="JPEG")
            status["preview"] = base64.b64encode(preview.getvalue()).decode()
            
        return status
        
    def get_report(self) -> Dict[str, Any]:
        """Get processing report"""
        if not self.enhanced_image or self.progress < 100:
            return {"error": "Processing not completed"}
            
        # Save processed image
        output = BytesIO()
        self.enhanced_image.save(output, format="JPEG")
        
        return {
            "processed_image": base64.b64encode(output.getvalue()).decode(),
            "processing_time": "2 seconds",  # In a real application, should record actual processing time
            "enhancement_params": self.configs["enhancement"]
        } 
    
    