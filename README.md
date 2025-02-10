# Multi-Application Web Service Framework

This is a scalable web service framework based on Flask/FastAPI, supporting the lifecycle management of multiple independent applications.

## Features

- Supports both Flask and FastAPI frameworks
- Unified application lifecycle management
- Supports multiple JSON configuration files
- Real-time status updates
- Supports binary data transmission, such as images
- Comprehensive test coverage
- Simple frontend interface

## Example Applications

1. **Image Processor**
   - Supports image uploads
   - Provides brightness, contrast, and sharpness adjustments
   - Real-time preview of processing effects
   - Generates processing reports

2. **Data Analyzer**
   - Supports numerical data analysis
   - Provides basic statistical calculations
   - Generates data distribution histograms
   - Outputs detailed analysis reports

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # Or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service
1. Using Flask(default)
```bash
python run.py
```
2. Using FastAPI
```bash
FRAMEWORK=fastapi python run.py
```

## API Endpoints

### Application Management

- `GET /api/apps` - Get a list of all applications
- `POST /api/apps` - Create a new application
- `GET /api/apps/types` - Retrieve available application types
- `DELETE /api/apps/{app_id}` - Delete an application

### Application Operations

- `POST /api/apps/{app_id}/config/{config_name}` - Upload the configuration file of an application
- `POST /api/apps/{app_id}/start` - Start an application
- `POST /api/apps/{app_id}/stop` - Stop an application
- `GET /api/apps/{app_id}/status` - Get the status of an application
- `GET /api/apps/{app_id}/report` - Get the report of an application

## Developing a new application

1. Inherit the `BaseApp` class

2. Implement the required abstract methods
validate_configs()
start()
stop()
get_status()
get_report()

3. Register the new application in `main.py`
```python
service.app_manager.register_app_type("your_app_name", YourAppClass)
```

## Testing

```bash
python -m pytest tests/test_apps.py -v
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

