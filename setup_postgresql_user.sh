#!/bin/bash

# Setup PostgreSQL user for Odoo

DB_USER="odoo"
DB_NAME="odoo_btp"

echo "Setting up PostgreSQL user: $DB_USER"
echo ""

# Create PostgreSQL user
echo "1. Creating PostgreSQL user '$DB_USER'..."
sudo -u postgres createuser -s $DB_USER 2>/dev/null || {
    echo "User may already exist, continuing..."
}

# Create database
echo "2. Creating database '$DB_NAME'..."
sudo -u postgres createdb $DB_NAME -O $DB_USER 2>/dev/null || {
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
        echo "Database already exists"
    else
        sudo -u postgres createdb $DB_NAME
    fi
}

# Update odoo.conf
echo "3. Updating odoo.conf..."
sed -i "s/^db_user = .*/db_user = $DB_USER/" odoo19/odoo.conf
sed -i "s/^db_password = .*/db_password = /" odoo19/odoo.conf

echo ""
echo "✓ PostgreSQL user setup complete!"
echo ""
echo "You can now run: ./init_database.sh"

