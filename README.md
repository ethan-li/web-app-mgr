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
- Runtime directory management for application files

## Example Applications

1. **Image Processor**
   - Supports image uploads
   - Provides brightness, contrast, and sharpness adjustments
   - Real-time preview of processing effects
   - Generates processing reports
   - Saves intermediate and final results

2. **Data Analyzer**
   - Supports numerical data analysis
   - Provides basic statistical calculations
   - Generates data distribution histograms
   - Outputs detailed analysis reports
   - Saves raw data and analysis results

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

1. Using Flask (default)
```bash
python run.py [--runtime-dir PATH]
```

2. Using FastAPI
```bash
FRAMEWORK=fastapi python run.py [--runtime-dir PATH]
```

### Command Line Arguments

- `--framework`: Web framework to use (default: flask, choices: flask, fastapi)
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 5000)
- `--runtime-dir`: Directory for runtime files (default: runtime)

### Environment Variables

The following environment variables can be used to override command line arguments:
- `FRAMEWORK`: Web framework to use
- `HOST`: Host to bind to
- `PORT`: Port to bind to
- `RUNTIME_DIR`: Directory for runtime files

## Runtime Directory Structure

The service creates a runtime directory for each application instance with the following structure:

```
runtime/
├── <app_id>/
    ├── config/         # Configuration files
    ├── intermediate/   # Intermediate processing files
    └── output/         # Final output files
```

- `config/`: Stores JSON configuration files uploaded by the user
- `intermediate/`: Stores intermediate files generated during processing
- `output/`: Stores final output files and reports

The runtime directory is automatically created and managed by the service. Each application instance gets its own subdirectory named with its unique ID. When an application is deleted, its directory and all contents are automatically cleaned up.

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

2. Implement the required abstract methods:
   - `validate_configs()`: Validate configuration files
   - `start()`: Start the application
   - `stop()`: Stop the application
   - `get_status()`: Get current status
   - `get_report()`: Get execution report

3. Use the provided file storage methods:
   - `upload_config(config_name, config_data)`: Upload configuration
   - `get_config(config_name)`: Get configuration
   - `save_intermediate_file(filename, content)`: Save intermediate file
   - `save_output_file(filename, content)`: Save output file

4. Register the new application in `main.py`:
```python
service.app_manager.register_app_type("your_app_name", YourAppClass)
```

## Testing

```bash
python -m pytest tests/test_apps.py -v
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

