from typing import Dict, Any, List
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request

from .web_service import WebService


class CreateAppRequest(BaseModel):
    app_type: str

class ConfigData(BaseModel):
    data: Dict[str, Any]

class FastAPIWebService(WebService):
    def __init__(self, runtime_dir: str = "runtime"):
        super().__init__(runtime_dir=runtime_dir)
        self.fastapi_app = FastAPI()
        
        # Set up static files and templates
        self.templates = Jinja2Templates(directory="app/templates")
        self.fastapi_app.mount("/static", StaticFiles(directory="app/static"), name="static")
        
        self._register_routes()
        
    def _register_routes(self):
        # Homepage route
        self.fastapi_app.get("/")(self.index)
        
        # Application management
        self.fastapi_app.post("/api/apps")(self.create_app)
        self.fastapi_app.delete("/api/apps/{app_id}")(self.delete_app)
        self.fastapi_app.get("/api/apps/types")(self.get_app_types)
        self.fastapi_app.get("/api/apps")(self.get_all_apps)
        
        # Application operations
        self.fastapi_app.post("/api/apps/{app_id}/config/{config_name}")(self.upload_config)
        self.fastapi_app.post("/api/apps/{app_id}/start")(self.start_app)
        self.fastapi_app.post("/api/apps/{app_id}/stop")(self.stop_app)
        self.fastapi_app.get("/api/apps/{app_id}/status")(self.get_app_status)
        self.fastapi_app.get("/api/apps/{app_id}/report")(self.get_app_report)
        
    async def index(self, request: Request):
        """Render homepage"""
        return self.templates.TemplateResponse("index.html", {"request": request})

    async def create_app(self, request: CreateAppRequest) -> Dict[str, Any]:
        try:
            app_id = self.app_manager.create_app_instance(request.app_type)
            return {"app_id": app_id}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    async def delete_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        self.app_manager.delete_app(app_id)
        return {"message": "Application deleted"}
        
    async def upload_config(self, app_id: str, config_name: str, config: ConfigData) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        app = self.app_manager.get_app(app_id)
        app.upload_config(config_name, config.data)
        return {"message": "Configuration uploaded"}
        
    async def start_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        app = self.app_manager.get_app(app_id)
        if app.is_running:
            raise HTTPException(status_code=400, detail="Application is already running")
            
        if not app.validate_configs():
            raise HTTPException(status_code=400, detail="Configuration validation failed")
            
        try:
            app.start()
            return {"message": "Application started"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Start failed: {str(e)}")
            
    async def stop_app(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        app = self.app_manager.get_app(app_id)
        if not app.is_running:
            raise HTTPException(status_code=400, detail="Application is not running")
            
        try:
            app.stop()
            return {"message": "Application stopped"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Stop failed: {str(e)}")
            
    async def get_app_status(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        app = self.app_manager.get_app(app_id)
        return app.get_status()
        
    async def get_app_report(self, app_id: str) -> Dict[str, Any]:
        error = self._get_app_or_error(app_id)
        if error:
            raise HTTPException(status_code=404, detail=error["error"])
            
        app = self.app_manager.get_app(app_id)
        return app.get_report()
        
    async def get_app_types(self) -> Dict[str, List[str]]:
        return {"app_types": list(self.app_manager.get_app_types().keys())}
        
    async def get_all_apps(self) -> Dict[str, Dict[str, Any]]:
        apps_info = {}
        for app_id, app in self.app_manager.get_all_apps().items():
            apps_info[app_id] = {
                "is_running": app.is_running,
                "status": app.get_status()
            }
        return {"apps": apps_info}
        
    def run(self, host: str = "0.0.0.0", port: int = 5000):
        import uvicorn
        uvicorn.run(self.fastapi_app, host=host, port=port) 

