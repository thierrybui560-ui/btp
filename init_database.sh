#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_DIR="$PROJECT_DIR/odoo19"
VENV_DIR="$ODOO_DIR/venv"
DB_NAME="odoo_btp"

echo "Initializing Odoo database: $DB_NAME"
echo "This will create the database and install base modules"
echo ""

# Check if Odoo is installed
ODOO_BIN="$ODOO_DIR/odoo/odoo-bin"
if [ ! -f "$ODOO_BIN" ]; then
    echo "Error: Odoo 19 not found in $ODOO_DIR/odoo/"
    echo "Expected file: $ODOO_BIN"
    echo ""
    echo "The Odoo directory exists but odoo-bin is missing."
    echo "This usually means the git checkout was incomplete."
    echo ""
    echo "Please run:"
    echo "  cd $ODOO_DIR/odoo"
    echo "  git checkout ."
    echo "  git pull"
    echo ""
    echo "Or reinstall:"
    echo "  rm -rf $ODOO_DIR/odoo"
    echo "  ./install_odoo19_local.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run: ./install_odoo19_local.sh"
    exit 1
fi

# Check PostgreSQL connection
echo "Checking PostgreSQL connection..."
if ! psql -U odoo -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "Error: Cannot connect to PostgreSQL"
    echo ""
    echo "Please ensure PostgreSQL is running and the 'odoo' role exists."
    echo "You can test with: psql -U odoo -d postgres -c \"SELECT 1;\""
    exit 1
fi
echo "✓ PostgreSQL connection OK"

# Check if database exists (using odoo superuser role)
if psql -U odoo -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "Database $DB_NAME already exists"
    read -p "Do you want to recreate it? (WARNING: This will delete all data!) [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        dropdb -U odoo --if-exists $DB_NAME
        createdb -U odoo -O odoo $DB_NAME 2>/dev/null || createdb -U odoo $DB_NAME
        echo "✓ Database recreated"
    else
        echo "Using existing database"
    fi
else
    echo "Creating database $DB_NAME..."
    createdb -U odoo -O odoo $DB_NAME 2>/dev/null || createdb -U odoo $DB_NAME
    if psql -U odoo -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw $DB_NAME; then
        echo "✓ Database created successfully"
    else
        echo "✗ Failed to create database"
        exit 1
    fi
fi

echo ""
echo "Initializing Odoo database (this may take a few minutes)..."
echo ""

cd $ODOO_DIR
source $VENV_DIR/bin/activate

# Run Odoo initialization
python3 $ODOO_BIN -c $ODOO_DIR/odoo.conf -d $DB_NAME --stop-after-init -i base

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Database initialized successfully!"
    echo ""
    echo "You can now start Odoo with: ./start_odoo.sh"
    echo "Then access it at: http://localhost:8069"
else
    echo ""
    echo "✗ Database initialization failed"
    echo "Check the logs for errors: tail -f $ODOO_DIR/logs/odoo.log"
    exit 1
fi
