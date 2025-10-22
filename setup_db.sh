#!/bin/bash
# PrismQ.IdeaInspiration.Sources.Content.Forums.RedditSource - Database Setup Script
# This script creates db.s3db in the user's working directory and sets up the RedditSource table
# Target: Linux (development support), Windows primary

echo "============================================================"
echo "PrismQ Reddit Source - Database Setup"
echo "============================================================"
echo

# Store the repository root (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set default Python executable
PYTHON_EXEC="python3"

# Check if Python executable exists
if ! command -v $PYTHON_EXEC &> /dev/null; then
    echo
    echo "[ERROR] Python executable '$PYTHON_EXEC' not found or not working."
    echo
    read -p "Please enter the Python executable path (e.g., python, python3): " PYTHON_INPUT
    
    PYTHON_EXEC="$PYTHON_INPUT"
    
    if ! command -v $PYTHON_EXEC &> /dev/null; then
        echo "[ERROR] Python executable '$PYTHON_EXEC' still not working."
        echo "[ERROR] Please install Python 3.8 or higher and try again."
        exit 1
    fi
fi

echo "[INFO] Using Python: $PYTHON_EXEC"
$PYTHON_EXEC --version
echo

# Find the nearest parent directory with "PrismQ" in its name
# This matches the behavior of config.py
PRISMQ_DIR=""
SEARCH_DIR="$(pwd)"

while [ "$SEARCH_DIR" != "/" ]; do
    # Check if current search directory contains "PrismQ" in its name
    if [[ "$(basename "$SEARCH_DIR")" == *"PrismQ"* ]]; then
        PRISMQ_DIR="$SEARCH_DIR"
        break
    fi
    # Move to parent directory
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -z "$PRISMQ_DIR" ]; then
    # No PrismQ directory found, use current directory as fallback
    USER_WORK_DIR="$(pwd)"
    echo "[INFO] No PrismQ directory found in path. Using current directory as working directory."
else
    # Found PrismQ directory, create working directory with _WD suffix
    PRISMQ_NAME="$(basename "$PRISMQ_DIR")"
    PRISMQ_PARENT="$(dirname "$PRISMQ_DIR")"
    USER_WORK_DIR="$PRISMQ_PARENT/${PRISMQ_NAME}_WD"
    
    echo "[INFO] Found PrismQ directory: $PRISMQ_DIR"
    echo "[INFO] Working directory (with _WD suffix): $USER_WORK_DIR"
fi

echo

# Database path (fixed to db.s3db)
DB_PATH="db.s3db"

# Create working directory if it doesn't exist
if [ ! -d "$USER_WORK_DIR" ]; then
    echo "[INFO] Creating working directory: $USER_WORK_DIR"
    mkdir -p "$USER_WORK_DIR"
fi

# Create the full database path
FULL_DB_PATH="$USER_WORK_DIR/$DB_PATH"
echo "[INFO] Database will be created at: $FULL_DB_PATH"
echo

# Check if Python dependencies are installed
echo "[INFO] Checking Python dependencies..."
$PYTHON_EXEC -c "import sqlalchemy" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] SQLAlchemy not found. Installing dependencies..."
    $PYTHON_EXEC -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies."
        echo "[ERROR] Please install dependencies manually: pip install -r requirements.txt"
        exit 1
    fi
fi

# Use the init_db.py script to create the database
echo "[INFO] Creating database and RedditSource table..."
$PYTHON_EXEC scripts/init_db.py --db-path "$FULL_DB_PATH"

if [ $? -ne 0 ]; then
    echo
    echo "[ERROR] Failed to create database or table."
    exit 1
fi

echo
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo
echo "Database Location: $FULL_DB_PATH"
echo "Table Created: RedditSource"
echo
echo "Table Schema:"
echo "  - id: INTEGER PRIMARY KEY AUTOINCREMENT"
echo "  - source: VARCHAR(100) NOT NULL (indexed)"
echo "  - source_id: VARCHAR(255) NOT NULL (indexed)"
echo "  - title: TEXT NOT NULL"
echo "  - description: TEXT"
echo "  - tags: TEXT (comma-separated)"
echo "  - score: FLOAT"
echo "  - score_dictionary: TEXT (JSON object with score components)"
echo "  - processed: BOOLEAN DEFAULT FALSE (indexed)"
echo "  - created_at: TIMESTAMP"
echo "  - updated_at: TIMESTAMP"
echo
echo "Indexes:"
echo "  - UNIQUE(source, source_id)"
echo "  - INDEX(score)"
echo "  - INDEX(created_at)"
echo "  - INDEX(processed)"
echo
echo "You can now use this database with PrismQ Reddit Source."
echo
