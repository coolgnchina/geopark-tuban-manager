# AGENTS.md

This file provides guidelines for AI coding agents operating in this repository.

## Project Overview

Flask-based web app for managing geological park violation records (图斑管理):
- **Framework**: Flask 2.3.0, Flask-SQLAlchemy 3.0.0
- **Database**: SQLite (database/tubans.db)
- **Frontend**: Bootstrap 5, jQuery, Chart.js
- **Data Processing**: pandas 2.0.0, openpyxl 3.1.0

## Build/Lint/Test Commands

### Running the Application

```bash
python app.py                    # Development (auto-reload)
python app_prod.py               # Production mode
start_optimized.bat              # Windows: Production start
restart_full.bat                 # Windows: Full restart
```

### Testing

No formal test framework. Test files are standalone scripts:

```bash
python test_export.py            # Export functionality (requires running server)
python test_icons.py             # Icon test

# To add pytest:
pip install pytest
pytest                           # Run all tests
pytest path/to/test.py           # Run specific test
pytest -v                        # Verbose output
```

### Code Quality

```bash
pip install flake8 black mypy
flake8 . --max-line-length=100   # Linting
black . --line-length 100        # Formatting
mypy .                           # Type checking
```

## Code Style Guidelines

### Imports

Standard → Third-party → Local. Blank lines between groups. No wildcard imports.

```python
# Correct
import os
from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from models import db
from models.tuban import Tuban
from routes.tuban import tuban_bp

# Incorrect
from flask import *
from datetime import *
import models.tuban
```

### Formatting

- **Line length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Blank lines**: 2 between top-level defs, 1 between class methods
- **No trailing whitespace**

### Types

Type hints optional but recommended:

```python
def get_tuban_by_id(tuban_id: int) -> Tuban | None:
    return Tuban.query.get(tuban_id)

def format_date(date_obj: datetime | None) -> str:
    if not date_obj:
        return '-'
    return date_obj.strftime('%Y-%m-%d')
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables/Functions | snake_case | `tuban_code`, `format_date()` |
| Classes | PascalCase | `Tuban`, `RectifyRecord` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |
| Private methods | `_leading_underscore()` | `_validate_input()` |
| DB columns | snake_case | `created_at`, `is_deleted` |

### Error Handling

Never use bare `except:`. Catch specific exceptions. Log errors.

```python
# Correct
try:
    tuban = Tuban.query.get(id)
    if not tuban:
        raise ValueError(f"图斑不存在: {id}")
except SQLAlchemyError as e:
    db.session.rollback()
    current_app.logger.error(f"数据库错误: {e}")
    raise
```

### Database Queries (SQLAlchemy)

```python
# Standard pattern
tuban = Tuban.query.filter_by(id=id, is_deleted=0).first()

# Complex query
from sqlalchemy import and_, or_
results = Tuban.query.filter(
    and_(
        Tuban.is_deleted == 0,
        Tuban.rectify_status.in_(['未整改', '整改中'])
    )
).all()
```

### Flask Patterns

- Use Blueprint for routes (see `routes/` directory)
- Access config via `current_app.config`
- Template globals registered in `create_app()`

### File Organization

```
project/
├── app.py              # Application factory
├── config.py           # Configuration
├── init_db.py          # DB initialization
├── models/             # SQLAlchemy models
│   ├── __init__.py     # db instance
│   └── tuban.py        # Tuban model
├── routes/             # Blueprint routes
│   ├── tuban.py        # /tuban endpoints
│   ├── stats.py        # /stats endpoints
│   └── system.py       # /system endpoints
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, images
└── utils/              # Helpers
```

### Database Migrations

```bash
python init_db.py       # Initialize/recreate DB
# To modify schema: edit model, delete tubans.db, run init_db.py
```

### Jinja2 Templates

- Extend `base.html` for consistent layout
- Use block tags: `{% block content %}{% endblock %}`
- Call template globals: `format_date()`, `get_status_color()`
- No complex logic in templates
