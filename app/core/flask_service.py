from typing import Dict, Any

from flask import Flask, request, jsonify, render_template

from .web_service import WebService

class FlaskWebService(WebService):
    def __init__(self):
        super().__init__()
        self.flask_app = Flask(__name__, 
                             template_folder='../templates',  # Set template directory
                             static_folder='../static')       # Set static file directory
        self._register_routes()
        
    def _register_routes(self):
        # Homepage route
        self.flask_app.route('/')(self.index)
        
        # Application management
        self.flask_app.route('/api/apps', methods=['POST'])(self.create_app)
        self.flask_app.route('/api/apps/<app_id>', methods=['DELETE'])(self.delete_app)
        self.flask_app.route('/api/apps/types', methods=['GET'])(self.get_app_types)
        self.flask_app.route('/api/apps', methods=['GET'])(self.get_all_apps)
        
        # Application operations
        self.flask_app.route('/api/apps/<app_id>/config/<config_name>', methods=['POST'])(self.upload_config)
        self.flask_app.route('/api/apps/<app_id>/start', methods=['POST'])(self.start_app)
        self.flask_app.route('/api/apps/<app_id>/stop', methods=['POST'])(self.stop_app)
        self.flask_app.route('/api/apps/<app_id>/status', methods=['GET'])(self.get_app_status)
        self.flask_app.route('/api/apps/<app_id>/report', methods=['GET'])(self.get_app_report)
        
    def index(self):
        """Render homepage"""
        return render_template('index.html')

    def create_app(self) -> Dict[str, Any]:
        data = request.get_json()
        app_type = data.get('app_type')
        if not app_type:
            return jsonify({"error": "Missing app_type parameter"}), 400
            
        try:
            app_id = self.app_manager.create_app_instance(app_type)
            return jsonify({"app_id": app_id})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    def delete_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        self.app_manager.delete_app(app_id)
        return jsonify({"message": "Application deleted"})
        
    def upload_config(self, app_id: str, config_name: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        config_data = request.get_json()
        if not config_data:
            return jsonify({"error": "Missing configuration data"}), 400
            
        app = self.app_manager.get_app(app_id)
        app.upload_config(config_name, config_data)
        return jsonify({"message": "Configuration uploaded"})
        
    def start_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        app = self.app_manager.get_app(app_id)
        if app.is_running:
            return jsonify({"error": "Application is already running"}), 400
            
        if not app.validate_configs():
            return jsonify({"error": "Configuration validation failed"}), 400
            
        try:
            app.start()
            return jsonify({"message": "Application started"})
        except Exception as e:
            return jsonify({"error": f"Start failed: {str(e)}"}), 500
            
    def stop_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        app = self.app_manager.get_app(app_id)
        if not app.is_running:
            return jsonify({"error": "Application is not running"}), 400
            
        try:
            app.stop()
            return jsonify({"message": "Application stopped"})
        except Exception as e:
            return jsonify({"error": f"Stop failed: {str(e)}"}), 500
            
    def get_app_status(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        app = self.app_manager.get_app(app_id)
        return jsonify(app.get_status())
        
    def get_app_report(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            return jsonify(error), 404
            
        app = self.app_manager.get_app(app_id)
        return jsonify(app.get_report())
        
    def get_app_types(self) -> Dict[str, Any]:
        return jsonify({"app_types": list(self.app_manager.get_app_types().keys())})
        
    def get_all_apps(self) -> Dict[str, Any]:
        apps_info = {}
        for app_id, app in self.app_manager.get_all_apps().items():
            apps_info[app_id] = {
                "is_running": app.is_running,
                "status": app.get_status()
            }
        return jsonify({"apps": apps_info})
        
    def run(self, host: str = "0.0.0.0", port: int = 5000):
        self.flask_app.run(host=host, port=port) 

        