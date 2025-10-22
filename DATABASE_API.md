# Reddit Source Database API

This document describes the database API and model implementation for the Reddit Source module, following the same pattern as the YouTube Shorts Source implementation.

## Overview

The Reddit Source uses SQLAlchemy ORM to provide a clean, type-safe database interface for storing and managing Reddit post data.

## Database Schema

### RedditSource Table

The main table for storing Reddit post data:

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key (auto-increment) | Yes (PK) |
| `source` | VARCHAR(100) | Source platform (e.g., 'reddit') | Yes |
| `source_id` | VARCHAR(255) | Unique Reddit post ID | Yes |
| `title` | TEXT | Post title | No |
| `description` | TEXT | Post content/description | No |
| `tags` | TEXT | Comma-separated tags | No |
| `score` | FLOAT | Calculated quality score | Yes |
| `score_dictionary` | TEXT | JSON string with score components | No |
| `processed` | BOOLEAN | Processing status flag | Yes |
| `created_at` | DATETIME | Record creation timestamp | Yes |
| `updated_at` | DATETIME | Record update timestamp | No |

**Unique Constraint**: `(source, source_id)` - prevents duplicate posts

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

#### Using setup scripts (recommended):

**Linux/Mac:**
```bash
./setup_db.sh
```

**Windows:**
```batch
setup_db.bat
```

#### Using Python directly:

```bash
python scripts/init_db.py --db-path /path/to/database.s3db
```

## API Usage

### Basic Example

```python
from Model.db_context import DBContext

# Initialize database
db = DBContext("reddit.db")

# Create a record
record = db.create(
    source='reddit',
    source_id='r/python_abc123',
    title='Best Python libraries for 2025',
    description='Discussion about top Python libraries',
    tags='python,libraries,tools',
    score=95.5,
    score_dictionary={
        'upvotes': 1500,
        'comments': 250,
        'awards': 12
    }
)

# Read a record
post = db.read('reddit', 'r/python_abc123')
print(post.title)
print(post.get_score_dict())

# Update a record
updated = db.update(
    source='reddit',
    source_id='r/python_abc123',
    score=96.0,
    processed=True
)

# Upsert (insert or update)
post = db.upsert(
    source='reddit',
    source_id='r/python_abc123',
    title='Updated Title',
    score=97.0
)

# List records
posts = db.list_all(limit=10, order_by='score', ascending=False)
for post in posts:
    print(f"{post.title} - Score: {post.score}")

# Count records
total = db.count()
reddit_count = db.count_by_source('reddit')

# Delete a record
success = db.delete('reddit', 'r/python_abc123')

# Close connection
db.close()
```

### Using Context Manager

```python
from Model.db_context import DBContext

with DBContext("reddit.db") as db:
    # Database operations here
    post = db.create(
        source='reddit',
        source_id='test_id',
        title='Test Post'
    )
    # Connection automatically closed
```

### Working with Score Dictionary

```python
# Create with score dictionary
post = db.create(
    source='reddit',
    source_id='post_123',
    title='Example Post',
    score_dictionary={
        'upvotes': 1000,
        'comments': 100,
        'awards': 5,
        'engagement_rate': 0.85
    }
)

# Get score dictionary
score_data = post.get_score_dict()
print(score_data['upvotes'])  # 1000

# Set score dictionary
post.set_score_dict({
    'upvotes': 1100,
    'comments': 110
})
```

### Converting to Dictionary

```python
post = db.read('reddit', 'post_123')
post_dict = post.to_dict()

# Returns:
# {
#     'id': 1,
#     'source': 'reddit',
#     'source_id': 'post_123',
#     'title': 'Example Post',
#     'description': None,
#     'tags': None,
#     'score': None,
#     'score_dictionary': '{"upvotes": 1000, ...}',
#     'processed': False,
#     'created_at': '2025-10-22T06:51:46.081791',
#     'updated_at': '2025-10-22T06:51:46.081795'
# }
```

## DBContext Methods

### CRUD Operations

- `create(source, source_id, title, description=None, tags=None, score=None, score_dictionary=None)` - Create new record
- `read(source, source_id)` - Read record by source and source_id
- `read_by_id(record_id)` - Read record by database ID
- `update(source, source_id, **fields)` - Update existing record
- `upsert(source, source_id, title, **fields)` - Insert or update record
- `delete(source, source_id)` - Delete record

### Query Operations

- `list_all(limit=None, order_by='score', ascending=False)` - List all records
- `count()` - Get total record count
- `count_by_source(source)` - Count records by source
- `clear_all()` - Delete all records (returns count deleted)

### Connection Management

- `close()` - Close database connection
- `__enter__()` / `__exit__()` - Context manager support

## Model Methods

### RedditSource Model

- `to_dict()` - Convert model to dictionary
- `get_score_dict()` - Get score_dictionary as Python dict
- `set_score_dict(score_dict)` - Set score_dictionary from Python dict
- `__repr__()` - String representation

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=Model --cov-report=html
```

## Example Script

See `example_api_usage.py` for a complete working example demonstrating all API features.

```bash
python example_api_usage.py
```

## Backward Compatibility

The `database.py` module provides a compatibility wrapper that maintains the original `Database` class interface while using the new ORM models internally. This ensures existing code continues to work without modifications.

## Architecture

```
┌─────────────────────────────────────┐
│  Application Code                   │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼──────────┐
│ database.py│    │  Model/         │
│ (compat)   │    │  - DBContext    │
└───┬────────┘    │  - RedditSource │
    │             │  - base         │
    └─────────────┴─────────────────┘
                  │
    ┌─────────────▼──────────────────┐
    │  SQLAlchemy ORM                │
    └─────────────┬──────────────────┘
                  │
    ┌─────────────▼──────────────────┐
    │  SQLite Database               │
    │  (RedditSource table)          │
    └────────────────────────────────┘
```

## Files

- `Model/base.py` - SQLAlchemy base configuration
- `Model/reddit_source.py` - RedditSource ORM model
- `Model/db_context.py` - Database context with CRUD operations
- `Model/__init__.py` - Model exports
- `database.py` - Backward compatibility wrapper
- `scripts/init_db.py` - Database initialization script
- `setup_db.sh` / `setup_db.bat` - Database setup scripts
- `tests/test_model.py` - Comprehensive test suite
- `example_api_usage.py` - API usage examples

## License

Same as the main project.
