#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ODOO_DIR="$PROJECT_DIR/odoo19"
VENV_DIR="$ODOO_DIR/venv"

if [ ! -f "$ODOO_DIR/odoo/odoo-bin" ]; then
    echo "Error: Odoo 19 not found in $ODOO_DIR/odoo/"
    echo ""
    echo "Please run the installation script first:"
    echo "  ./install_odoo19_local.sh"
    echo ""
    echo "Or if installation failed on optional packages:"
    echo "  ./continue_installation.sh"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found"
    echo "Please run: ./install_odoo19_local.sh"
    exit 1
fi

echo "Starting Odoo 19..."
echo "Project directory: $PROJECT_DIR"
echo "Odoo directory: $ODOO_DIR"
echo ""
echo "Access Odoo at: http://localhost:8069"
echo "Press Ctrl+C to stop"
echo ""

cd $ODOO_DIR
source $VENV_DIR/bin/activate
$VENV_DIR/bin/python3 $ODOO_DIR/odoo/odoo-bin -c $ODOO_DIR/odoo.conf "$@"

