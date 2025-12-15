# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Development mode (with debug enabled)
python app.py

# Production mode (optimized performance)
python app_prod.py

# Using batch scripts
start_optimized.bat      # Production environment
restart_full.bat         # Complete restart with cleanup
restart_en.bat           # Quick restart
```

### Database Operations
```bash
# Initialize database with sample data
python init_db.py

# Database file location: database/tubans.db
```

### Managing Static Resources
```bash
# Download all CDN resources to local (if CDN fails)
python download_static.py

# Update template CDN links to local paths
python update_templates.py
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt
```

## High-Level Architecture

### Application Structure
This is a Flask web application using the factory pattern with blueprint-based modular architecture:

- **Factory Pattern**: `create_app()` function in app.py creates and configures the Flask instance
- **Blueprint Organization**: Routes are organized into three main blueprints:
  - `tuban_bp`: 图斑管理 (Tuban management)
  - `stats_bp`: 统计分析 (Statistics)
  - `system_bp`: 系统设置 (System settings)

### Data Model Architecture
The system centers around the **Tuban** (图斑) model with 38 fields organized into 7 logical groups:
1. Basic information (图斑编号, 地质公园, 功能区, etc.)
2. Construction entity information
3. Discovery and verification details
4. Problem and violation information
5. Rectification tracking
6. Penalty information
7. Management metadata

Supporting models:
- **Dictionary**: Maintains dropdown options for various fields
- **RectifyRecord**: Tracks rectification progress with timestamps

### Key Design Patterns

1. **Soft Delete Pattern**: All models use `is_deleted` field for logical deletion
2. **Dictionary Pattern**: Drop-down values stored in Dictionary model, referenced by `dict_type`
3. **Factory Pattern**: Application creation centralized in `create_app()` function
4. **Blueprint Pattern**: Modular route organization with URL prefixes
5. **Template Inheritance**: Base template (`base.html`) provides common layout and navigation

### Frontend Architecture
- **Bootstrap 5**: Main CSS framework with responsive design
- **Bootstrap Icons**: Icon system (with Unicode fallback for reliability)
- **jQuery**: DOM manipulation and AJAX
- **Chart.js**: Data visualization for statistics pages
- **Template System**: Jinja2 with template inheritance

### Configuration Management
- Single configuration class in `config.py` using inheritance
- Environment-specific settings (debug mode, database paths, etc.)
- Centralized configuration for file uploads, pagination, and Excel handling

### Excel Integration
- Import/Export functionality for图斑 data
- Supports both .xlsx and .xls formats
- Data validation during import
- Template generation for consistent data format

### Security Considerations
- Session-based authentication with before_request hook
- Whitelist approach for public endpoints
- Default credentials: admin/admin123 (should be changed in production)

### Performance Optimizations
- Production mode disables debug and auto-reload
- Threading enabled for concurrent request handling
- Local static resource hosting to avoid CDN issues
- Pagination for large datasets (20 items per page default)