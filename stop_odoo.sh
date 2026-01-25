#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_DIR="$PROJECT_DIR/odoo19"

echo "Stopping Odoo 19..."
echo ""

# Find Odoo processes
ODOO_PIDS=$(pgrep -f "$ODOO_DIR/odoo/odoo-bin.*-c.*$ODOO_DIR/odoo.conf" 2>/dev/null)

if [ -z "$ODOO_PIDS" ]; then
    echo "No Odoo processes found running."
    exit 0
fi

echo "Found Odoo processes:"
ps -fp $ODOO_PIDS 2>/dev/null | grep -v "PID" || echo "$ODOO_PIDS"
echo ""

# Try graceful shutdown first (SIGTERM)
echo "Sending termination signal..."
kill -TERM $ODOO_PIDS 2>/dev/null

# Wait up to 10 seconds for processes to stop
for i in {1..10}; do
    sleep 1
    REMAINING=$(pgrep -f "$ODOO_DIR/odoo/odoo-bin.*-c.*$ODOO_DIR/odoo.conf" 2>/dev/null)
    if [ -z "$REMAINING" ]; then
        echo "✓ Odoo stopped gracefully"
        exit 0
    fi
done

# Force kill if still running
REMAINING=$(pgrep -f "$ODOO_DIR/odoo/odoo-bin.*-c.*$ODOO_DIR/odoo.conf" 2>/dev/null)
if [ -n "$REMAINING" ]; then
    echo "Processes still running, forcing shutdown..."
    kill -9 $REMAINING 2>/dev/null
    sleep 1
    
    # Verify they're stopped
    STILL_RUNNING=$(pgrep -f "$ODOO_DIR/odoo/odoo-bin.*-c.*$ODOO_DIR/odoo.conf" 2>/dev/null)
    if [ -z "$STILL_RUNNING" ]; then
        echo "✓ Odoo stopped (forced)"
    else
        echo "✗ Some processes could not be stopped: $STILL_RUNNING"
        exit 1
    fi
fi

