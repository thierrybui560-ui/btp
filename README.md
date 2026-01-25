# Odoo BTP Prospecting Module

## Quick Start

### Start Odoo
```bash
./start_odoo.sh
```

Then access at: http://localhost:8069

### Stop Odoo
```bash
./stop_odoo.sh
```

**Login:**
- Email: `admin@btp.local`
- Password: `admin123`

### Initialize Database (if needed)
```bash
./init_database.sh
```

## Project Structure

- `btp_prospecting/` - BTP Prospecting & Lead Management module
- `odoo19/` - Odoo 19 installation
- `odoo19/addons/btp_prospecting/` - Module installed in Odoo

## Database Configuration

- Database: `odoo_btp`
- User: `odoo`
- Host: `localhost:5432`

## Module Features

See `btp_prospecting/README.md` for detailed module documentation.

